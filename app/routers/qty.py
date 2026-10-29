from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, oauth2, schemas


router = APIRouter(
    prefix="/qty", 
    tags=["Qty"] 
)


@router.get("/", response_model=List[schemas.QtyResponse])
def get_quantities(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # get top level quantities - children and entries will load via SQLAlchemy relationships
    qty = db.query(models.Qty).filter(models.Qty.parent_id == None).all()
    return qty

@router.get("/{id}", response_model=schemas.QtyResponse)
def get_quantity(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    qty = db.query(models.Qty).filter(models.Qty.id == id).first()
    if not qty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quantity with id {id} was not found.")
    return qty

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.QtyResponse)
def create_quantity(qty: schemas.QtyCreate, db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    # optional check if parent id exists if provided
    if qty.parent_id:
        parent = db.query(models.Qty).filter(models.Qty.id==qty.parent_id).first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Parent quantity with id {qty.parent_id} does not exist.")

    # check if user has qty permission
    user_perms = [p.name for p in current_user.permissions]
    if not "admin" in user_perms and not "qty" in user_perms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"You do not have the required 'qty' permission to perform this action")

    # create new quantity
    new_qty = models.Qty(**qty.model_dump())
    db.add(new_qty)
    db.commit()
    db.refresh(new_qty)
    return new_qty

@router.put("/{id}", response_model=schemas.QtyResponse)
def update_quantity(id: int, qty: schemas.QtyUpdate, db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    # check if user has qty permission
    user_perms = [p.name for p in current_user.permissions]
    if not "admin" in user_perms and not "qty" in user_perms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"You do not have the required 'qty' permission to perform this action")

    # check that the qty to update exists
    query = db.query(models.Qty).filter(models.Qty.id == id)
    check_qty = query.first()

    if not check_qty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Quantity with id {id} not found")

    query.update(qty.model_dump(exclude_unset=True), synchronize_session=False)
    db.commit()
    db.refresh(check_qty)
    return check_qty


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quantity(id:int, db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    # check if user has qty permission
    user_perms = [p.name for p in current_user.permissions]
    if not "admin" in user_perms and not "qty" in user_perms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"You do not have the required 'qty' permission to perform this action")

    query = db.query(models.Qty).filter(models.Qty.id==id)
    check_qty = query.first()

    if not check_qty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quantity with id {id} not found.")

    query.delete(synchronize_session=False)
    db.commit()
    return


# -------- time-distributed entries endpoints -------------------------------------------------

@router.post("/{qty_id}/entries", status_code=status.HTTP_201_CREATED, response_model=schemas.QtyEntryResponse)
def create_quantity_entry(qty_id:int, entry:schemas.QtyEntryCreate, db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    # check if user has qty permission
    user_perms = [p.name for p in current_user.permissions]
    if not "admin" in user_perms and not "qty" in user_perms:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You do not have the required 'qty' permission to perform this action")

    # check if target qty exists
    check_qty = db.query(models.Qty).filter(models.Qty.id==qty_id).first()
    if not check_qty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quantity with id {qty_id} does not exist.")

    # add record to quantity entry
    new_entry = models.QtyEntry(qty_id=qty_id, **entry.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@router.put("/entries/{entry_id}", response_model=schemas.QtyEntryResponse)
def update_quantity_entry(entry_id:int, entry_update:schemas.QtyEntryUpdate, db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    # check if user has qty permission
    user_perms = [p.name for p in current_user.permissions]
    if not "admin" in user_perms and not "qty" in user_perms:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You do not have the required 'qty' premission to perform this action")

    # check if the entry to be updated exists
    query = db.query(models.QtyEntry).filter(models.QtyEntry.id==entry_id)
    entry = query.first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quantity with entry {entry_id} not found")

    query.update(entry_update.model_dump(exclude_unset=True), synchronize_session=False)
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quantity_entry(entry_id:int, db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    # check if user has qty permission
    user_perms = [p.name for p in current_user.permissions]
    if not "admin" in user_perms and not "qty" in user_perms:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You do not have the required 'qty' permission to perform this action")

    # check if entry exists
    query = db.query(models.QtyEntry).filter(models.QtyEntry.id==entry_id)
    entry = query.first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quantity entry with id {entry_id} not found.")

    query.delete(synchronize_session=False)
    db.commit()
    return


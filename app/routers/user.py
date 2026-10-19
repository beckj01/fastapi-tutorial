from typing import List
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, utils, oauth2 # note two dots tells python to look in the parent directory

router = APIRouter(
    prefix = "/users", 
    tags = ["Users"]
)
# the keyword @app is replaced with @router as we are using the fastAPI router, to connect this route to the main.py file where app is stored


@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).order_by(models.User.id).all()
    return users
    

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist")
    return user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password

    # add the new user to the database table
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.put("/{id}", response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    update_query = db.query(models.User).filter(models.User.id==id)
    update_user = update_query.first()

    # check if the user id exists
    if update_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist.")

    # check so that only the logged in user can only update their own username
    if update_user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You cannot update another users profile")

    update_query.update(user.model_dump(), synchronize_session=False)
    db.commit()

    return update_query.first()
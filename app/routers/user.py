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


@router.get("/", response_model=List[schemas.UserResponsePermissions])
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


@router.post("/{id}/permissions", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponsePermissions)
def add_permission_to_user(id: int, permission: schemas.PermissionCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id==id).first()
    perm = db.query(models.Permission).filter(models.Permission.name == permission.name).first()

    # check if logged in user has permission to add user permissions
    current_user_permissions = [p.name for p in current_user.permissions]
    if not "admin" in current_user_permissions and not "user_profiles" in current_user_permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You do not have the required permissions to assign permissions.")

    # check if target user exists
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist.")
        
    # check if the permission exists
    if not perm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Permission {permission.name} does not exist.")

    # check if user already has this permission assigned
    if perm in user.permissions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User already has the {permission.name} permission")

    # add the permission
    user.permissions.append(perm)
    db.commit()

    return user
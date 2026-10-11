from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import oauth2, schemas, models, utils


router = APIRouter(
    tags = ["Authentication"]
)

#def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)): # function header using your own pydantic schema model
@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==user_credentials.username).first()

    # return a 404 if the user does not exist in the database
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # verify the password is correct
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # create a token & return to the user
    #   Note: you can include whatever information you wish in the payload. Could be username, email, roles, permissions etc
    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

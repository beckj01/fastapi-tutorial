from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# these are the pydantic models for data validation into & out of the database

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

    class Config:
        #orm_mode = True # the old naming of this property
        from_attributes = True

class PostCreate(PostBase): # extends the PostBase class, hence inherits all of the properties (column) from PostBase
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

class PostOut(BaseModel):
    Post: PostResponse
    votes: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    short_name: Optional[str] = None
    display_name: Optional[str] = None
    pc_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    short_name: Optional[str] = None
    display_name: Optional[str]  = None
    pc_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    short_name: Optional[str] = None
    display_name: Optional[str] = None
    pc_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    direction: int


# Notes:
# age: Optional[int] = None - This field is NOT required, if omitted detaults to None
# age: Optional[int]        - This field is REQUIRED to be present, but the value can be None
# age: int                  - this field is REQUIRED and cannot be None
#
#
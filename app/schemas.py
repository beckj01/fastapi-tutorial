from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

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

class UserResponsePermissions(UserResponse):
    permissions: List[PermissionResponse] = []
    


class UserLogin(BaseModel):
    email: EmailStr
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class PermissionCreate(BaseModel):
    name: str

class PermissionResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True # allows Pydantic to read SQLAlchemy models


class Vote(BaseModel):
    post_id: int
    direction: int


class QtyEntryCreate(BaseModel):
    we_date: datetime
    cumulative_plan: float = 0
    period_plan: float = 0
    cumulative_actual: float = 0
    period_actual: float = 0
    cumulative_forecast: float = 0
    period_forecast: float = 0

class QtyEntryUpdate(BaseModel):
    we_date: Optional[datetime] = None
    cumulative_plan: Optional[float] = None
    period_plan: Optional[float] = None
    cumulative_actual: Optional[float] = None
    period_actual: Optional[float] = None
    cumulative_forecast: Optional[float] = None
    period_forecast: Optional[float] = None

class QtyEntryResponse(QtyEntryCreate):
    id: int
    qty_id: int

    class Config:
        from_attributes = True


class QtyCreate(BaseModel):
    name: str
    UoM: str
    area: Optional[str] = None
    owner_id: Optional[int] = None
    parent_id: Optional[int] = None

class QtyUpdate(BaseModel):
    name: Optional[str] = None
    UoM: Optional[str] = None
    area: Optional[str] = None
    owner_id: Optional[int] = None
    parent_id: Optional[int] = None

class QtyResponse(BaseModel):
    id: int
    name: str
    UoM: str
    area: Optional[str] = None
    owner_id: Optional[int] = None
    parent_id: Optional[int] = None
    entries: List[QtyEntryResponse] = []
    children: List["QtyResponse"] = []

    class Config:
        from_attributes = True # allows Pydantic to read SQLAlchemy models

# required for Pydantic v2 recursive self-referencing models
QtyResponse.model_rebuild()

# Notes:
# age: Optional[int] = None - This field is NOT required, if omitted detaults to None
# age: Optional[int]        - This field is REQUIRED to be present, but the value can be None
# age: int                  - this field is REQUIRED and cannot be None
#
#
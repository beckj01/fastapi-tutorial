from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

# these are the ORM managed database table definitions

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default="TRUE")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    # note for ForeignKeys you reference the table name, not the class name
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = False) 

    # relationships ------
    owner = relationship("User") # this time you reference the class, not the table name


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    short_name = Column(String)
    display_name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    phone_number = Column (String)


class Vote(Base):
    __tablename__ = "votes"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)




from sqlalchemy import Column, Integer, String, Date
from app.db import Base
from pydantic import BaseModel
from datetime import date
from typing import Optional

# ----------------- SQLAlchemy ORM Models -----------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    team = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Leave(Base):
    __tablename__ = "leave"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    comment = Column(String, nullable=True)

# ----------------- Pydantic Schemas -----------------

class LeaveRead(BaseModel):
    id: int
    name: str
    date: date
    comment: Optional[str]

    class Config:
        orm_mode = True

class LeaveCreate(BaseModel):
    name: str
    date: date
    comment: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    id: int
    name: str
    designation: str
    team: str
    email: str
    username: str
    password: str  # plain password, will be hashed in backend

    class Config:
        orm_mode = True


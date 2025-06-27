from sqlalchemy import Column, String, Boolean,Integer, ForeignKey
from .db import Base

# 2 tables - onr for user and one for to do taks for user

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority=Column(Integer)
    is_completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
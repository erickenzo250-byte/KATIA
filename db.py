### FILE: db.py
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    password: str
    gender: str
    dob: str
    bio: Optional[str] = ""
    profile_pic: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Like(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_user_id: int = Field(foreign_key="user.id")
    to_user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine("sqlite:///dating.db", echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

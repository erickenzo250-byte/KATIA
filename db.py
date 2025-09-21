# db.py
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"   # ✅ explicit
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    gender: str
    dob: str
    bio: Optional[str] = None
    profile_pic: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Like(SQLModel, table=True):
    __tablename__ = "likes"   # ✅ explicit
    id: Optional[int] = Field(default=None, primary_key=True)
    from_user_id: int = Field(foreign_key="users.id")
    to_user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"   # ✅ explicit
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="users.id")
    receiver_id: int = Field(foreign_key="users.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- DB setup ---
engine = create_engine("sqlite:///dating.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

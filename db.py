from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
import streamlit as st

# ------------------------
# Models
# ------------------------

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    likes: list["Like"] = Relationship(back_populates="user")
    messages: list["Message"] = Relationship(back_populates="sender")


class Like(SQLModel, table=True):
    __tablename__ = "likes"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="likes")


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="users.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sender: User = Relationship(back_populates="messages")


# ------------------------
# Database Setup (Streamlit Optimized)
# ------------------------

DATABASE_URL = "sqlite:///database.db"   # Change to Postgres/MySQL if needed


@st.cache_resource
def get_engine():
    """Create and cache the database engine (runs only once)."""
    return create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Create all database tables (if not exist)."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Yield a database session for queries inside Streamlit."""
    engine = get_engine()
    with Session(engine) as session:
        yield session

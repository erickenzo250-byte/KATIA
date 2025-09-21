from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session

# ------------------------
# User Model
# ------------------------
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    likes: list["Like"] = Relationship(back_populates="user")
    messages: list["Message"] = Relationship(back_populates="sender")


# ------------------------
# Like Model
# ------------------------
class Like(SQLModel, table=True):
    __tablename__ = "likes"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="likes")


# ------------------------
# Message Model
# ------------------------
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="users.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sender: User = Relationship(back_populates="messages")


# ------------------------
# Database Setup
# ------------------------

DATABASE_URL = "sqlite:///database.db"   # ✅ change this if using Postgres/MySQL

engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Provide a new session for database operations."""
    with Session(engine) as session:
        yield session

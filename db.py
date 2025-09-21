# db.py

from contextlib import contextmanager
from sqlmodel import Session

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

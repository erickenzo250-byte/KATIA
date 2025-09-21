import streamlit as st
from db import init_db, get_session, User, Like, Message
from datetime import datetime
import random

# --- Prevent reinitializing DB on every Streamlit reload ---
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True

st.set_page_config(page_title="Dating Admin", layout="wide")
st.title("💻 Dating Site Admin Dashboard")

# --- Sidebar navigation ---
menu = ["Users", "Likes", "Messages"]
choice = st.sidebar.radio("Navigate", menu)

# --- Reset Database Button ---
if st.sidebar.button("⚠️ Reset Database"):
    with get_session() as db:
        db.query(Like).delete()
        db.query(Message).delete()
        db.query(User).delete()
        db.commit()
    st.sidebar.success("Database has been reset!")

# --- Dummy data helpers ---
def add_dummy_user():
    usernames = ["alice", "bob", "charlie", "diana", "eva"]
    name = random.choice(usernames) + str(random.randint(100, 999))
    user = User(
        username=name,
        email=f"{name}@test.com",
        password="hashedpassword",
        gender=random.choice(["Male", "Female"]),
        dob="1990-01-01",
        bio="This is a dummy bio.",
        profile_pic=None,
        created_at=datetime.utcnow()
    )
    with get_session() as db:
        db.add(user)
        db.commit()

def add_dummy_like():
    with get_session() as db:
        users = db.query(User).all()
        if len(users) < 2:
            return False
        u1, u2 = random.sample(users, 2)
        like = Like(from_user_id=u1.id, to_user_id=u2.id, created_at=datetime.utcnow())
        db.add(like)
        db.commit()
        return True

def add_dummy_message():
    with get_session() as db:
        users = db.query(User).all()
        if len(users) < 2:
            return False
        u1, u2 = random.sample(users, 2)
        msg = Message(
            sender_id=u1.id,
            receiver_id=u2.id,
            content=f"Hello from {u1.username} to {u2.username}",
            created_at=datetime.utcnow()
        )
        db.add(msg)
        db.commit()
        return True

# --- Page: Users ---
if choice == "Users":
    st.header("Users Table")
    if st.button("➕ Add Dummy User"):
        add_dummy_user()
        st.success("Dummy user added!")

    with get_session() as db:
        users = db.query(User).all()
        if users:
            st.dataframe([u.__dict__ for u in users])
        else:
            st.info("No users found.")

# --- Page: Likes ---
elif choice == "Likes":
    st.header("Likes Table")
    if st.button("➕ Add Dummy Like"):
        if add_dummy_like():
            st.success("Dummy like added!")
        else:
            st.warning("Need at least 2 users to create a like.")

    with get_session() as db:
        likes = db.query(Like).all()
        if likes:
            st.dataframe([l.__dict__ for l in likes])
        else:
            st.info("No likes found.")

# --- Page: Messages ---
elif choice == "Messages":
    st.header("Messages Table")
    if st.button("➕ Add Dummy Message"):
        if add_dummy_message():
            st.success("Dummy message added!")
        else:
            st.warning("Need at least 2 users to create a message.")

    with get_session() as db:
        messages = db.query(Message).all()
        if messages:
            st.dataframe([m.__dict__ for m in messages])
        else:
            st.info("No messages found.")

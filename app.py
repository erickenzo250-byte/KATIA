### FILE: app.py
import os
import streamlit as st
from db import init_db, get_session, User, Like, Message
from auth import hash_password, verify_password
from sqlmodel import select
from datetime import datetime

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

# --- Session State ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- Auth Pages ---
def register():
    st.header("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    dob = st.date_input("Date of Birth")
    if st.button("Register"):
        with get_session() as db:
            if db.exec(select(User).where(User.username == username)).first():
                st.error("Username taken")
            else:
                user = User(
                    username=username,
                    email=email,
                    password=hash_password(password),
                    gender=gender,
                    dob=str(dob),
                )
                db.add(user)
                db.commit()
                st.success("Registered! Please login.")

def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        with get_session() as db:
            user = db.exec(select(User).where(User.username == username)).first()
            if user and verify_password(password, user.password):
                st.session_state.user = user
                st.rerun()   # ✅ updated
            else:
                st.error("Invalid login")

def logout():
    st.session_state.user = None
    st.rerun()  # ✅ updated

# --- Features ---
def profile():
    st.header("My Profile")
    u = st.session_state.user
    with get_session() as db:
        user = db.get(User, u.id)
        st.text_input("Username", value=user.username, disabled=True)
        bio = st.text_area("Bio", value=user.bio or "")
        pic = st.file_uploader("Upload Profile Picture", type=["jpg","png"])
        if st.button("Save"):
            if pic:
                path = os.path.join(UPLOAD_DIR, f"user_{user.id}.png")
                with open(path, "wb") as f:
                    f.write(pic.read())
                user.profile_pic = path
            user.bio = bio
            db.add(user)
            db.commit()
            st.success("Updated!")

def browse():
    st.header("Browse Users")
    with get_session() as db:
        users = db.exec(select(User).where(User.id != st.session_state.user.id)).all()
        for u in users:
            with st.container():
                st.subheader(u.username)
                if u.profile_pic and os.path.exists(u.profile_pic):
                    st.image(u.profile_pic, width=100)
                st.write(u.bio or "")
                if st.button(f"Like {u.username}", key=f"like_{u.id}"):
                    like = Like(from_user_id=st.session_state.user.id, to_user_id=u.id)
                    db.add(like)
                    db.commit()
                    st.success("Liked!")

def chat():
    st.header("Chat")
    receiver = st.text_input("Chat with user id:")
    msg = st.text_input("Message")
    if st.button("Send"):
        with get_session() as db:
            db.add(Message(sender_id=st.session_state.user.id, receiver_id=int(receiver), content=msg))
            db.commit()
    # Load messages
    with get_session() as db:
        messages = db.exec(
            select(Message).where(
                ((Message.sender_id==st.session_state.user.id) & (Message.receiver_id==receiver)) |
                ((Message.sender_id==receiver) & (Message.receiver_id==st.session_state.user.id))
            ).order_by(Message.created_at)
        ).all()
        for m in messages:
            sender = "Me" if m.sender_id == st.session_state.user.id else f"User {m.sender_id}"
            st.write(f"{sender}: {m.content} ({m.created_at.strftime('%H:%M')})")

# --- Main ---
st.sidebar.title("Dating App")
if st.session_state.user:
    page = st.sidebar.radio("Menu", ["Profile", "Browse", "Chat", "Logout"])
    if page == "Profile":
        profile()
    elif page == "Browse":
        browse()
    elif page == "Chat":
        chat()
    elif page == "Logout":
        logout()
else:
    page = st.sidebar.radio("Auth", ["Login", "Register"])
    if page == "Login":
        login()
    elif page == "Register":
        register()

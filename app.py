### FILE: app.py
import os
import streamlit as st
from db import init_db, get_session, User, Like, Message

# --- Prevent reinitializing DB on every Streamlit reload ---
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True
import streamlit as st
from db import init_db, get_session, User, Like, Message
from sqlmodel import select
from datetime import datetime

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

# --- Force Admin Session ---
with get_session() as db:
    user = db.exec(select(User)).first()
    if not user:
        # create dummy admin user if DB is empty
        user = User(username="admin", email="admin@example.com", password="admin", gender="Other", dob="2000-01-01")
        db.add(user)
        db.commit()
        db.refresh(user)
    st.session_state.user = user

# --- Features ---
def profile():
    st.header("My Profile (Admin Mode)")
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
st.sidebar.title("Dating App (Admin Mode)")
page = st.sidebar.radio("Menu", ["Profile", "Browse", "Chat"])
if page == "Profile":
    profile()
elif page == "Browse":
    browse()
elif page == "Chat":
    chat()

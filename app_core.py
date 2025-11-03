import os
import streamlit as st
import mysql.connector
from dotenv import load_dotenv
from fungsi.encryption import hash_password, verify_password, AESCipher, BlowfishCipher

load_dotenv()


@st.cache_resource
def init_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "edu_secure")
    )


# initialize cipher singletons used by pages
aes_cipher = AESCipher(os.getenv("AES_KEY", "default_aes_key"))
blowfish_cipher = BlowfishCipher(os.getenv("BLOWFISH_KEY", "default_blowfish_key"))


def user_exists(username: str) -> bool:
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    return cursor.fetchone()[0] > 0


def register_user(username: str, password: str, role: str = 'mahasiswa'):
    if user_exists(username):
        return False, "Username already exists"
    hashed = hash_password(password)
    conn = init_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (username, hashed, role))
        conn.commit()
        return True, "User registered"
    except Exception as e:
        return False, str(e)


def login_user(username: str, password: str) -> bool:
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user and verify_password(password, user['password']):
        st.session_state.logged_in = True
        st.session_state.user_role = user.get('role')
        st.session_state.username = username
        return True
    return False
"""
Placeholder module: core functionality merged into `app.py`.

This file was kept for history during refactoring but is now intentionally empty to
avoid accidental imports. If you'd like to remove it from the repository entirely,
delete the file or run `git rm app_core.py`.

All active logic lives in `app.py`.
"""

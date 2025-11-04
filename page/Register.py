import streamlit as st
import koneksi as conn
import hashlib
import os

def register():
    st.title("📝 Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    re_password = st.text_input("Re-enter Password", type="password", key="register_re_password")

    if st.button("Register", key="register_button"):
        if not username or not password or not re_password:
            st.error("Username and password cannot be empty.")
            return
        if password != re_password:
            st.error("Passwords do not match.")
            return

        query = conn.run_query("SELECT * FROM user WHERE username = %s;", (username,), fetch=True)
        if query is not None and not query.empty:
            st.error("Username already exists.")
        else:
            salt = os.urandom(16)
            hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

            success = conn.run_query(  # <-- Tangkap hasilnya
                "INSERT INTO user (username, password, salt) VALUES (%s, %s, %s);",
                (username, hashed_password, salt),
                fetch=False
            )
            
            # --- PERUBAHAN: Periksa apakah 'success' itu True ---
            if success:
                st.success("Registration successful.")
            else:
                st.error("Registration failed. Please try again or contact support.")
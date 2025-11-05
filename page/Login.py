import streamlit as st
import hashlib
import hmac
import koneksi as conn

def login():
    st.title("🔐 Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if not username or not password:
            st.error("Masukkan username dan password.")
            return

        query = conn.run_query(
            "SELECT username, password, salt FROM user WHERE username = %s;",
            (username,),
            fetch=True
        )

        if query is not None and not query.empty:
            stored_hash = query.iloc[0]["password"]
            stored_salt = query.iloc[0]["salt"]

            computed_hash = hashlib.pbkdf2_hmac(
                'sha256', password.encode(), stored_salt, 100000
            )

            if hmac.compare_digest(computed_hash, stored_hash):
                st.session_state['sudah_login'] = True
                st.session_state['username'] = username
                st.success("✅ Login berhasil.")
                st.rerun()
            else:
                st.error("❌ Username atau password salah.")
        else:
            st.error("❌ Username atau password salah.")

import streamlit as st
import koneksi as conn
import hashlib
import os
from fungsi import db_encrypt

def register():
    st.title("📝 Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    re_password = st.text_input("Re-enter Password", type="password", key="register_re_password")

    if st.button("Register", key="register_button"):
        if not username or not password or not re_password:
            st.error("Username dan password tidak boleh kosong.")
            return
        if password != re_password:
            st.error("Password tidak cocok.")
            return

        # Ambil semua username, dekripsi, dan cek
        all_users_df = conn.run_query("SELECT username FROM user;", fetch=True)
        username_exists = False
        if all_users_df is not None and not all_users_df.empty:
            for enc_username_bytes in all_users_df['username']:
                try:
                    decrypted_username = db_encrypt.decrypt_db_string(enc_username_bytes)
                    if decrypted_username == username:
                        username_exists = True
                        break
                except Exception as e:
                    print(f"Error decrypting username during registration check: {e}")
        
        if username_exists:
            st.error("Username sudah terdaftar.")
        else:
            salt = os.urandom(16)
            hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            # Enkripsi username sebelum insert
            encrypted_username = db_encrypt.encrypt_db_string(username)

            success = conn.run_query( 
                "INSERT INTO user (username, password, salt) VALUES (%s, %s, %s);",
                (encrypted_username, hashed_password, salt),
                fetch=False
            )
            
            if success:
                st.success("Register berhasil.")
            else:
                st.error("Register gagal. Silahkan coba lagi.")
import streamlit as st
import hashlib
import hmac
import koneksi as conn
from fungsi import db_encrypt

def login():
    st.title("🔐 Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if not username or not password:
            st.error("Masukkan username dan password.")
            return

        # Ambil semua user, dekripsi username untuk cari match
        all_users_df = conn.run_query("SELECT id_user, username, password, salt FROM user;", fetch=True)
        
        found_user = None
        if all_users_df is not None and not all_users_df.empty:
            for _, row in all_users_df.iterrows():
                try:
                    decrypted_username = db_encrypt.decrypt_db_string(row['username'])
                    if decrypted_username == username:
                        found_user = row
                        break
                except Exception as e:
                    print(f"Error decrypting username during login: {e}")

        if found_user is not None:
            stored_hash = found_user["password"]
            stored_salt = found_user["salt"]

            computed_hash = hashlib.pbkdf2_hmac(
                'sha256', password.encode(), stored_salt, 100000
            )

            if hmac.compare_digest(computed_hash, stored_hash):
                st.session_state['sudah_login'] = True
                # Simpan username plaintext di session state
                st.session_state['username'] = username 
                st.success("✅ Login berhasil.")
                st.rerun()
            else:
                st.error("❌ Username atau password salah.")
        else:
            st.error("❌ Username atau password salah.")
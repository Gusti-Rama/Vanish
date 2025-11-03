import streamlit as st
from app_core import login_user, register_user

st.set_page_config(page_title="Edu Secure System", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None


if not st.session_state.logged_in:
    st.title("Edu Secure — Login / Register")
    mode = st.radio("Mode", ["Login", "Register"], index=0, horizontal=True)

    if mode == "Login":
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if login_user(username, password):
                    st.success("Login berhasil!")
                    st.experimental_rerun()
                else:
                    st.error("Username atau password salah")
    else:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            role = st.selectbox("Role", ["mahasiswa", "dosen"], index=0)
            submit_reg = st.form_submit_button("Register")

            if submit_reg:
                if not new_username or not new_password:
                    st.error("Username dan password harus diisi")
                elif new_password != confirm_password:
                    st.error("Password tidak cocok")
                else:
                    ok, msg = register_user(new_username, new_password, role)
                    if ok:
                        st.success("Register berhasil — silahkan kembali ke Login")
                    else:
                        st.error(f"Register gagal: {msg}")

    st.info("Setelah login, Anda akan dapat menggunakan halaman di sidebar: Pesan, Data Mahasiswa, Dokumen, Sertifikat.")
    st.stop()


st.title("Edu Secure System")
st.markdown(
    """
    Welcome back — use the sidebar to navigate the application pages in this order:

    1. Messages
    2. Student Data
    3. Documents
    4. Certificates

    All functional pages live in the `pages/` directory and share helpers from `app_core.py`.
    """
)

st.success(f"Login sebagai: {st.session_state.username} — role: {st.session_state.user_role}")

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.experimental_rerun()
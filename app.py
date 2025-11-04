import streamlit as st
from page import Login, Register, Chat

st.set_page_config(page_title="Vanish")
st.title("Vanish")
st.text("Vanish is a secure messaging app that allows you to send and receive messages securely.")

# Hide sidebar when not logged in
if 'sudah_login' not in st.session_state:
    st.session_state['sudah_login'] = False

if st.session_state['sudah_login']:
    # Show sidebar only when logged in
    username = st.session_state['username']
    st.sidebar.success(f"Hai, {username}")
    page = st.sidebar.radio("Go To", ["Text", "Steganography", "File"])
    if st.sidebar.button("Logout"):
        st.session_state['sudah_login'] = False
        st.rerun()
    Chat.menu(page) 
   
else:
    # No sidebar when not logged in - show tabs instead
    st.markdown("<style> section[data-testid='stSidebar'] { display: none; } </style>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        Login.login()
    
    with tab2:
        Register.register()

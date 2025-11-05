import streamlit as st
from page import login, register, chat, demo,file,stego, home

if 'sudah_login' not in st.session_state:
    st.session_state['sudah_login'] = False

layout_mode = "wide" if st.session_state['sudah_login'] else "centered"
st.set_page_config(
    page_title="Vanish",
    page_icon="🤫",
    layout=layout_mode
)

if st.session_state['sudah_login']:
    
    username = st.session_state['username']

    st.sidebar.title("Vanish")
    st.sidebar.subheader(f"Selamat Datang, {username}!")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigasi", 
        ["🏠 Dashboard","💬 Chat", "🧪 Demo Super-Enkripsi", "🔒 Enkripsi File", "🖼️ Steganography"],  
        key="nav_radio"
    )
    
    if page == "🏠 Dashboard":
        home.home()
    elif page == "💬 Chat":
        chat.chat_page()
    elif page == "🧪 Demo Super-Enkripsi":
        demo.demo_page() 
    elif page == "🔒 Enkripsi File":
        file.file_page()
    elif page == "🖼️ Steganography": 
        stego.stego_page()
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state['sudah_login'] = False
        st.rerun()

else:
    st.markdown("""
    <style>
        section[data-testid='stSidebar'] { display: none; }
        [data-testid="stMainMenu"] { display: none; }
        footer { visibility: hidden; }

        [data-testid="stAppViewContainer"] {
            background-color: #111111;
        }

        .block-container {
            padding-top: 2rem; 
            padding-bottom: 2rem;
        } 	

        h1 {
            text-align: center; 
            color: #ffffff;
        }
        .app-subheader {
             text-align: center; 
             color: #aaaaaa; 
             font-size: 1.1rem;
             margin-bottom: 2rem; 
        }

        .form-container {
             background-color: #262730; 
             border-radius: 15px; 	 	 
             border: 1px solid #444; 	 	 
             box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3); 
             overflow: hidden; 
        }

        .tab-content {
            padding: 0.1rem 2.5rem 2.5rem 2.5rem; /* Atas, Kanan, Bawah, Kiri */
        }
        
        .tab-content h1,
        .tab-content h2,
        .tab-content h3 {
            margin-top: 0;
            padding-top: 0;
        }
        
        [data-testid="stTabs"] {
            margin-top: 0; 
        }

        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #ffffff; 
            background-color: #262730; 
            border-bottom: 3px solid #ffffff; /* Garis bawah putih tebal */
        }

        [data-testid="stTextInput"] label, 
        [data-testid="stDateInput"] label {
            color: #e0e0e0 !important; 
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Vanish")
    
    st.markdown(
        "<p class='app-subheader'>"
        "Vanish adalah sebuah aplikasi chat terenkripsi untuk mengirim dan menerima pesan dengan aman."
        "</p>", 
        unsafe_allow_html=True
    )
    
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        login.login() 
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        register.register() 
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
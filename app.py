import streamlit as st
from page import Login, Register, Chat

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
    
    st.sidebar.title(f"Selamat Datang, {username}!")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigasi", 
        ["💬 Chat", "🖼️ Steganography", "🔒 File Encryption"], 
        key="nav_radio"
    )
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state['sudah_login'] = False
        st.rerun()
    
    page_map = {
        "💬 Chat": "Chat",
        "🖼️ Steganography": "Steganography",
        "🔒 File Encryption": "File"
    }
    
    Chat.menu(page_map[page]) #

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
        "Vanish is a secure messaging app that allows you to send and receive messages securely."
        "</p>", 
        unsafe_allow_html=True
    )
    
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        Login.login() 
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        Register.register() 
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
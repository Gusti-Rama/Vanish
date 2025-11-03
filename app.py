import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd
from fungsi.encryption import hash_password, verify_password, AESCipher, BlowfishCipher
from fungsi.caesar import caesar_encrypt, caesar_decrypt
from fungsi.xor import xor_encrypt, xor_decrypt
from fungsi.steganography import encode_image, decode_image
import tempfile
import base64

# Load environment variables
load_dotenv()

# Database connection
@st.cache_resource
def init_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "edu_secure")
    )

# Initialize encryption objects
aes_cipher = AESCipher(os.getenv("AES_KEY", "default_aes_key"))
blowfish_cipher = BlowfishCipher(os.getenv("BLOWFISH_KEY", "default_blowfish_key"))

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

def login(username, password):
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and verify_password(password, user['password']):
        st.session_state.logged_in = True
        st.session_state.user_role = user['role']
        st.session_state.username = username
        return True
    return False


def user_exists(username):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    return cursor.fetchone()[0] > 0


def register_user(username, password, role='mahasiswa'):
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

def main():
    st.title("Edu Secure System")
    
    if not st.session_state.logged_in:
        # Choose between Login and Register
        mode = st.radio("Mode", ["Login", "Register"], index=0, horizontal=True)

        if mode == "Login":
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    if login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

        else:  # Register
            with st.form("register_form"):
                new_username = st.text_input("Choose a username")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm password", type="password")
                role = st.selectbox("Role", ["mahasiswa", "dosen"], index=0)
                submit_reg = st.form_submit_button("Register")

                if submit_reg:
                    if not new_username or not new_password:
                        st.error("Username and password are required")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        ok, msg = register_user(new_username, new_password, role)
                        if ok:
                            st.success("Registration successful — please login")
                            # pre-fill login fields
                            st.experimental_set_query_params()
                        else:
                            st.error(f"Registration failed: {msg}")
    else:
        # Sidebar navigation
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        page = st.sidebar.selectbox(
            "Navigation",
            ["Student Data", "Messages", "Documents", "Certificates"]
        )
        
        if page == "Student Data":
            show_student_data()
        elif page == "Messages":
            show_messages()
        elif page == "Documents":
            show_documents()
        elif page == "Certificates":
            show_certificates()
            
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()

def show_student_data():
    st.header("Student Academic Records")
    
    if st.session_state.user_role in ['admin', 'dosen']:
        # Fetch and decrypt student data
        conn = init_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_data")
        students = cursor.fetchall()
        
        # Decrypt data
        decrypted_data = []
        for student in students:
            decrypted_data.append({
                'nim': student['nim'],
                'nama': aes_cipher.decrypt(student['nama']),
                'nilai': aes_cipher.decrypt(student['nilai'])
            })
        
        df = pd.DataFrame(decrypted_data)
        st.dataframe(df)
        
        # Add new student data form
        if st.session_state.user_role == 'admin':
            with st.form("add_student"):
                st.subheader("Add New Student")
                nim = st.text_input("NIM")
                nama = st.text_input("Name")
                nilai = st.text_input("Grade")
                
                if st.form_submit_button("Add Student"):
                    try:
                        cursor.execute(
                            "INSERT INTO student_data (nim, nama, nilai) VALUES (%s, %s, %s)",
                            (nim, aes_cipher.encrypt(nama), aes_cipher.encrypt(nilai))
                        )
                        conn.commit()
                        st.success("Student added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def show_messages():
    st.header("Secure Messages")
    
    # Message sending form
    with st.form("send_message"):
        recipient = st.selectbox("Recipient", ["admin", "dosen"])
        message = st.text_area("Message")
        
        if st.form_submit_button("Send Message"):
            # Apply super encryption (Caesar + XOR)
            caesar_text = caesar_encrypt(message, shift=3)
            final_encrypted = xor_encrypt(caesar_text, key="secret_key")
            
            conn = init_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender, recipient, message) VALUES (%s, %s, %s)",
                (st.session_state.username, recipient, final_encrypted)
            )
            conn.commit()
            st.success("Message sent!")
    
    # Display received messages
    st.subheader("Received Messages")
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM messages WHERE recipient = %s ORDER BY created_at DESC",
        (st.session_state.username,)
    )
    messages = cursor.fetchall()
    
    for msg in messages:
        # Decrypt message (XOR then Caesar)
        xor_decrypted = xor_decrypt(msg['message'], key="secret_key")
        final_decrypted = caesar_decrypt(xor_decrypted, shift=3)
        
        st.text_area(
            f"From: {msg['sender']} at {msg['created_at']}",
            final_decrypted,
            disabled=True
        )

def show_documents():
    st.header("Secure Documents")
    
    # Upload document
    uploaded_file = st.file_uploader("Upload Document (PDF)", type=['pdf'])
    if uploaded_file:
        # Encrypt file content
        file_content = uploaded_file.read()
        encrypted_content = blowfish_cipher.encrypt_file(file_content)
        
        conn = init_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (filename, content, uploaded_by) VALUES (%s, %s, %s)",
            (uploaded_file.name, encrypted_content, st.session_state.username)
        )
        conn.commit()
        st.success("Document uploaded and encrypted!")
    
    # Display documents
    st.subheader("Available Documents")
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    
    for doc in documents:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📄 {doc['filename']}")
        with col2:
            if st.button("Download", key=f"doc_{doc['id']}"):
                # Decrypt document
                decrypted_content = blowfish_cipher.decrypt_file(doc['content'])
                # Create download link
                b64 = base64.b64encode(decrypted_content).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{doc["filename"]}">Click to download</a>'
                st.markdown(href, unsafe_allow_html=True)

def show_certificates():
    st.header("Digital Certificates")
    
    # Upload certificate with watermark
    uploaded_image = st.file_uploader("Upload Certificate (JPG/PNG)", type=['jpg', 'png'])
    if uploaded_image:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(uploaded_image.getvalue())
            temp_path = tmp_file.name
        
        # Add university authenticity mark using steganography
        secret_data = f"Authenticated by University on {pd.Timestamp.now()}"
        output_path = temp_path.replace('.png', '_marked.png')
        
        if encode_image(temp_path, secret_data, output_path):
            st.success("Certificate processed successfully!")
            
            # Display original and processed images
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Certificate")
                st.image(temp_path)
            with col2:
                st.subheader("Processed Certificate")
                st.image(output_path)
                
                # Add verify button
                if st.button("Verify Authenticity"):
                    try:
                        hidden_data = decode_image(output_path)
                        st.info(f"Certificate Authenticity: {hidden_data}")
                    except Exception as e:
                        st.error("Could not verify certificate authenticity")
            
            # Cleanup temporary files
            os.unlink(temp_path)
            os.unlink(output_path)

if __name__ == "__main__":
    main()
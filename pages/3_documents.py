import streamlit as st
import base64
from app_core import init_connection, blowfish_cipher

st.set_page_config(page_title="Dokumen", layout="centered")
st.title("Dokumen Mahasiswa")

if not st.session_state.get('logged_in'):
    st.warning("Anda harus login untuk mengunggah atau mengunduh dokumen.")
else:
    uploaded_file = st.file_uploader("Upload Dokumen (PDF)", type=['pdf'])
    if uploaded_file:
        file_content = uploaded_file.read()
        encrypted_content = blowfish_cipher.encrypt_file(file_content)
        conn = init_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (filename, content, uploaded_by) VALUES (%s, %s, %s)",
            (uploaded_file.name, encrypted_content, st.session_state.username)
        )
        conn.commit()
        st.success("Dokumen berhasil diunggah dan dienkripsi!")

    st.markdown("---")
    st.subheader("Dokumen Tersedia")
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents ORDER BY id DESC")
    documents = cursor.fetchall()

    for doc in documents:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📄 {doc['filename']} — diupload oleh {doc['uploaded_by']}")
        with col2:
            if st.button("Download", key=f"doc_{doc['id']}"):
                try:
                    decrypted_content = blowfish_cipher.decrypt_file(doc['content'])
                    b64 = base64.b64encode(decrypted_content).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{doc["filename"]}">Download</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error("Tidak dapat mendekripsi dokumen")

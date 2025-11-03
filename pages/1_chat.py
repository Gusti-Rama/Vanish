import streamlit as st
from app_core import init_connection
from fungsi.caesar import caesar_encrypt, caesar_decrypt
from fungsi.xor import xor_encrypt, xor_decrypt

st.set_page_config(page_title="Chat", layout="centered")
st.title("Chat Secure")

if not st.session_state.get('logged_in'):
    st.warning("Anda harus login untuk mengirim dan membaca pesan. Silahkan login terlebih dahulu.")
else:
    with st.form("send_message"):
        recipient = st.selectbox("Penerima", ["admin", "dosen", "mahasiswa"])
        message = st.text_area("Pesan")
        if st.form_submit_button("Kirim Pesan"):
            caesar_text = caesar_encrypt(message, shift=3)
            final_encrypted = xor_encrypt(caesar_text, key="secret_key")
            conn = init_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender, recipient, message) VALUES (%s, %s, %s)",
                (st.session_state.username, recipient, final_encrypted)
            )
            conn.commit()
            st.success("Pesan terkirim!")

    st.markdown("---")
    st.subheader("Pesan Masuk")
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM messages WHERE recipient = %s ORDER BY created_at DESC",
        (st.session_state.username,)
    )
    messages = cursor.fetchall()

    for msg in messages:
        try:
            xor_decrypted = xor_decrypt(msg['message'], key="secret_key")
            final_decrypted = caesar_decrypt(xor_decrypted, shift=3)
        except Exception:
            final_decrypted = "<decryption error>"
        st.text_area(f"From: {msg['sender']} at {msg['created_at']}", final_decrypted, disabled=True)

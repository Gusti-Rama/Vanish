import streamlit as st
import koneksi as conn
from datetime import datetime
from fungsi import caesar, xor, rsa
import html
from fungsi import db_encrypt

def get_user_id(username):
    query = conn.run_query(
        "SELECT id_user FROM user WHERE username = %s;",
        (username,),
        fetch=True
    )
    if query is not None and not query.empty:
        return int(query.iloc[0]['id_user'])
    return None


def load_user_chats(user_id):
    query = conn.run_query(
        """
        SELECT DISTINCT u.id_user, u.username,
               (SELECT MAX(created_at) FROM text 
                WHERE (sender_id = %s AND receiver_id = u.id_user) 
                   OR (sender_id = u.id_user AND receiver_id = %s)) as last_message_time
        FROM user u
        WHERE u.id_user != %s
          AND (u.id_user IN (SELECT receiver_id FROM text WHERE sender_id = %s)
               OR u.id_user IN (SELECT sender_id FROM text WHERE receiver_id = %s))
        ORDER BY last_message_time DESC;
        """,
        (user_id, user_id, user_id, user_id, user_id),
        fetch=True
    )
    
    if query is not None and not query.empty:
        return query.to_dict('records')
    return []


def load_messages(user_id1, user_id2):
    query = conn.run_query(
        """
        SELECT t.id_text, t.message, t.sender_id, t.receiver_id, t.created_at,
               u1.username as sender_username, u2.username as receiver_username
        FROM text t
        LEFT JOIN user u1 ON t.sender_id = u1.id_user
        LEFT JOIN user u2 ON t.receiver_id = u2.id_user
        WHERE (t.sender_id = %s AND t.receiver_id = %s)
           OR (t.sender_id = %s AND t.receiver_id = %s)
        ORDER BY t.created_at ASC;
        """,
        (user_id1, user_id2, user_id2, user_id1),
        fetch=True
    )
    
    if query is not None and not query.empty:
        messages = []
        for _, row in query.iterrows():
            message_content = row['message']
            
            # Dekripsi data dari DB (ChaCha20)
            try:
                if isinstance(message_content, bytes):
                    decrypted_db_bytes = db_encrypt.decrypt_db_data(message_content)
                    message_content = decrypted_db_bytes.decode('utf-8')
                else:
                    message_content = message_content.decode('utf-8')
            except Exception as e:
                print(f"Gagal dekripsi pesan DB (ID: {row['id_text']}): {e}")
                message_content = "[Data terenkripsi korup atau kunci salah]"
                
            messages.append({
                'id_text': row['id_text'],
                'message': message_content, 
                'sender_id': row['sender_id'],
                'receiver_id': row['receiver_id'],
                'sender_username': row['sender_username'],
                'receiver_username': row['receiver_username'],
                'created_at': row['created_at']
            })
        return messages
    return []

def delete_chat_history(user_id1, user_id2):
    query = """
        DELETE FROM text 
        WHERE (sender_id = %s AND receiver_id = %s) 
           OR (sender_id = %s AND receiver_id = %s);
    """
    success = conn.run_query(
        query,
        (user_id1, user_id2, user_id2, user_id1),
        fetch=False 
    )
    return success

def chat_page():    
    current_username = st.session_state.get('username')
    if not current_username:
        st.error("Mohon login terlebih dahulu!")
        return
    
    current_user_id = get_user_id(current_username)
    if not current_user_id:
        st.error("User tidak ditemukan!")
        return
    
    if 'active_chat' not in st.session_state:
        st.session_state['active_chat'] = None
    
    # BALIKIN KUNCI KE SESSION_STATE
    if 'chat_caesar_shift' not in st.session_state:
        st.session_state['chat_caesar_shift'] = 7
    if 'chat_xor_key' not in st.session_state:
        st.session_state['chat_xor_key'] = "69"

    chats = load_user_chats(current_user_id)
    
    with st.sidebar:
        st.header("💬 Chats")
        st.subheader("Kontak")
        
        if not chats:
            st.info("Belum ada chat. Tambahkan kontak baru untuk memulai")
        else:
            for chat in chats:
                chat_username = chat['username']
                is_active = st.session_state['active_chat'] == chat_username
                
                if is_active:
                    st.markdown(
                        f"""<div style="background-color: #1f77b4; color: white; padding: 10px; border-radius: 8px; margin: 5px 0; cursor: pointer;">
                            <strong>{chat_username}</strong>
                        </div>""", unsafe_allow_html=True)
                else:
                    if st.button(f"💬 {chat_username}", key=f"chat_{chat_username}", use_container_width=True):
                        st.session_state['active_chat'] = chat_username
                        st.rerun()
        
        st.subheader("Tambah Chat Baru")
        new_chat_username = st.text_input("Masukkan username untuk chat", key="new_chat_input", placeholder="Username...")

        if st.button("➕ Tambah Chat", key="add_chat_button"):
            if new_chat_username:
                new_chat_username = new_chat_username.strip()
                if new_chat_username == current_username:
                    st.error("Anda tidak dapat chat ke diri sendiri!")
                elif any(chat['username'] == new_chat_username for chat in chats):
                    st.warning("Chat dengan pengguna ini sudah ada!")
                    st.session_state['active_chat'] = new_chat_username
                    st.rerun()
                else:
                    other_user_id = get_user_id(new_chat_username)
                    if other_user_id:
                        st.session_state['active_chat'] = new_chat_username
                        st.success(f"Chat dengan {new_chat_username} ditambahkan!")
                        st.rerun()
                    else:
                        st.error("User tidak ditemukan!")

    if st.session_state['active_chat']:
        display_chat_area(st.session_state['active_chat'], current_user_id, current_user_id)
    else:
        st.title("Vanish Chat")
        st.info("Pilih User untuk di chat.")


def display_chat_area(chat_username, current_user_id, current_user_id_for_key):    
    st.title(f"💬 Chat with {chat_username}")
    
    other_user_id = get_user_id(chat_username)
    if not other_user_id:
        st.error("User tidak ditemukan!")
        return
    
    messages = load_messages(current_user_id, other_user_id)
    
    st.subheader("Messages")
    st.info("Pesan ditampilkan sebagai ciphertext. Gunakan 'Demo Super-Enkripsi' untuk mendekripsi.")
    messages_container = st.container(height=400) 
    
    with messages_container:
        if messages:
            for msg in messages:
                display_message(msg, st.session_state.get('username', 'You'))
        else:
            st.info(f"Belum ada chat dengan {chat_username}!")
    
    st.divider()

    st.subheader("Pengaturan Kunci Enkripsi (Untuk Mengirim)")
    st.warning("Pastikan pengirim dan penerima menyetujui kunci yang SAMA persis.")
    
    col_key1, col_key2 = st.columns(2)
    with col_key1:
        st.number_input(
            "Caesar Shift (1-25)", 
            min_value=1, 
            max_value=25, 
            key="chat_caesar_shift" # pake kunci dari session_state
        )
    with col_key2:
        st.text_input(
            "Kunci XOR (Teks)", 
            key="chat_xor_key", # pake kunci dari session_state
            placeholder="Contoh: rahasia123"
        )

    st.subheader("Kirim Pesan")
    
    message_text = st.text_area(
        "Tulis Pesan Anda Di Sini", 
        key=f"message_input_{chat_username}",
        height=100,
        placeholder="Tulis pesan Anda di sini..."
    )
    
    col_send, col_clear = st.columns([4, 1])

    with col_send:
        st.button(
            "📤 Kirim Pesan",
            key=f"send_button_{chat_username}",
            on_click=send_message,
            args=(chat_username, current_user_id, other_user_id, message_text),
            use_container_width=True,
            help="Teks akan dienkripsi menggunakan kunci di atas. Jika Anda menempelkan ciphertext, teks akan dienkripsi ganda."
        )
    
    with col_clear:
        st.button(
            "🗑️ Hapus Teks",
            key=f"clear_button_{chat_username}", 
            on_click=clear_all_inputs, 
            args=(chat_username,), 
            use_container_width=True,
            help="Menghapus teks yang akan dikirim"
        )

    with st.expander("⚠️ Hapus Riwayat Chat"):
        st.warning("PERINGATAN: Tindakan ini akan menghapus seluruh riwayat chat INI (untuk Anda DAN penerima) secara permanen dari server.")
        
        if st.button("Hapus Riwayat Chat Ini (Tidak bisa dibatalkan)", key=f"delete_chat_{chat_username}", use_container_width=True):
            success = delete_chat_history(current_user_id, other_user_id)
            if success:
                st.success("Riwayat chat berhasil dihapus.")
                st.rerun()
            else:
                st.error("Gagal menghapus riwayat chat.")


def display_message(message, current_username):
    sender_username = message.get('sender_username', '')
    message_content = message.get('message', '') 
    timestamp = message.get('created_at', '')
    
    if isinstance(timestamp, datetime):
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    elif timestamp:
        timestamp = str(timestamp)
    
    is_own = sender_username == current_username
    safe_content = html.escape(str(message_content))
    ciphertext_style = "word-wrap: break-word; font-family: 'Courier New', monospace; font-size: 0.9em; opacity: 0.9;"
    
    if is_own:
        st.markdown(
            f"""
            <div style="background-color: #007bff; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%; text-align: right;">
                <strong>You</strong><br>
                <div style="{ciphertext_style}">
                    {safe_content}
                </div>
                <br><small style="opacity: 0.8;">{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            f"""
            <div style="background-color: #e9ecef; color: black; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;">
                <strong>{sender_username}</strong><br>
                <div style="{ciphertext_style} color: #333;">
                    {safe_content}
                </div>
                <br><small style="opacity: 0.6;">{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)

def send_message(chat_username, sender_id, receiver_id, message_text):    
    if not message_text or not message_text.strip():
        st.warning("Please enter a message!")
        return
    
    full_message = message_text.strip()
    
    # Ambil kunci dari session_state
    caesar_shift = st.session_state.get('chat_caesar_shift',    )
    xor_key = st.session_state.get('chat_xor_key', "69")
    if not xor_key: xor_key = "69" 

    # Super-Enkripsi
    encrypted_caesar = caesar.caesar_encrypt(full_message, caesar_shift) 
    encrypted_xor = xor.xor_encrypt(encrypted_caesar, xor_key) 
    encrypted_rsa = rsa.rsa_encrypt(encrypted_xor) 
    encrypted_message_str = ' '.join(map(str, encrypted_rsa)) # string

    # Enkrip DB (ChaCha20)
    message_bytes_for_db = encrypted_message_str.encode('utf-8')
    encrypted_payload_for_db = db_encrypt.encrypt_db_data(message_bytes_for_db)

    success = conn.run_query(
        "INSERT INTO text (message, sender_id, receiver_id) VALUES (%s, %s, %s);",
        (encrypted_payload_for_db, sender_id, receiver_id),
        fetch=False
    )
    
    if success:
        st.session_state[f"message_input_{chat_username}"] = ""
        st.success("Message sent!")
    else:
        st.error("Failed to send message. Please try again.")


def clear_all_inputs(chat_username):    
    text_key = f"message_input_{chat_username}"
    if text_key in st.session_state:
        st.session_state[text_key] = ""
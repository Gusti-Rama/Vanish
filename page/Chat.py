import streamlit as st
import koneksi as conn
from datetime import datetime

def get_user_id(username):
    """Get user ID from username"""
    query = conn.run_query(
        "SELECT id_user FROM user WHERE username = %s;",
        (username,),
        fetch=True
    )
    if query is not None and not query.empty:
        return int(query.iloc[0]['id_user'])
    return None


def load_user_chats(user_id):
    """Load all chats for a user (users they've messaged or been messaged by)"""
    # Get all unique users this user has conversations with
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
    """Load messages between two users"""
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
        # Convert message blob to string
        messages = []
        for _, row in query.iterrows():
            message_content = row['message']
            if isinstance(message_content, bytes):
                message_content = message_content.decode('utf-8')
            
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


def menu(page):
    """Main menu function that routes to different pages"""
    if page == "Chat":
        chat_interface()
    elif page == "Steganography":
        st.title("Steganography")
        st.info("Steganography feature coming soon...")
    elif page == "File":
        st.title("File")
        st.info("File feature coming soon...")


def chat_interface():
    """Main chat interface with sidebar for chat list and main chat area"""
    
    # Get current user ID
    current_username = st.session_state.get('username')
    if not current_username:
        st.error("Please log in first!")
        return
    
    current_user_id = get_user_id(current_username)
    if not current_user_id:
        st.error("User not found in database!")
        return
    
    if 'active_chat' not in st.session_state:
        st.session_state['active_chat'] = None
    
    # Load chats from database
    chats = load_user_chats(current_user_id)
    
    # Sidebar for chat list
    with st.sidebar:
        st.header("💬 Chats")
        
        # Add new chat section
        st.subheader("Add New Chat")
        new_chat_username = st.text_input(
            "Enter username to chat with",
            key="new_chat_input",
            placeholder="Username..."
        )
        
        if st.button("➕ Add Chat", key="add_chat_button"):
            if new_chat_username:
                new_chat_username = new_chat_username.strip()
                if new_chat_username == current_username:
                    st.error("You cannot chat with yourself!")
                elif any(chat['username'] == new_chat_username for chat in chats):
                    st.warning("Chat with this user already exists!")
                    st.session_state['active_chat'] = new_chat_username
                    st.rerun()
                else:
                    # Verify user exists in database
                    other_user_id = get_user_id(new_chat_username)
                    if other_user_id:
                        st.session_state['active_chat'] = new_chat_username
                        st.success(f"Chat with {new_chat_username} added!")
                        st.rerun()
                    else:
                        st.error("User not found!")
        
        st.divider()
        
        # Display existing chats
        st.subheader("Your Chats")
        
        if not chats:
            st.info("No chats yet. Add a new chat to get started!")
        else:
            for chat in chats:
                chat_username = chat['username']
                is_active = st.session_state['active_chat'] == chat_username
                
                # Style the chat box differently if active
                if is_active:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #1f77b4;
                            color: white;
                            padding: 10px;
                            border-radius: 8px;
                            margin: 5px 0;
                            cursor: pointer;
                        ">
                            <strong>{chat_username}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    if st.button(
                        f"💬 {chat_username}",
                        key=f"chat_{chat_username}",
                        use_container_width=True
                    ):
                        st.session_state['active_chat'] = chat_username
                        st.rerun()
    
    # Main chat area
    if st.session_state['active_chat']:
        display_chat_area(st.session_state['active_chat'], current_user_id)
    else:
        # Welcome screen when no chat is selected
        st.title("💬 Welcome to Chat")
        st.info("👈 Select a chat from the sidebar or add a new chat to get started!")
        
        # Show some stats or instructions
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chats", len(chats))
        with col2:
            st.metric("Active Chat", "None" if not st.session_state['active_chat'] else st.session_state['active_chat'])
        with col3:
            st.metric("Status", "Ready")


def display_chat_area(chat_username, current_user_id):
    """Display the main chat interface for a specific user"""
    
    st.title(f"💬 Chat with {chat_username}")
    
    # Get other user ID
    other_user_id = get_user_id(chat_username)
    if not other_user_id:
        st.error("User not found!")
        return
    
    # Load messages from database
    messages = load_messages(current_user_id, other_user_id)
    
    # Display chat messages
    st.subheader("Messages")
    
    # Container for messages
    messages_container = st.container()
    
    with messages_container:
        if messages:
            for msg in messages:
                display_message(msg, st.session_state.get('username', 'You'))
        else:
            st.info(f"No messages yet. Start chatting with {chat_username}!")
    
    st.divider()
    
    # Message input and file upload section
    st.subheader("Send Message")
    
    # Text input
    message_text = st.text_area(
        "Type your message",
        key=f"message_input_{chat_username}",
        height=100,
        placeholder="Type your message here..."
    )
    
    # File upload buttons row
    st.subheader("📎 Attach File")

    # Step 1: Choose file type
    file_type = st.selectbox(
        "Select file type to upload",
        options=["None", "Image", "Video", "Audio", "Document"],
        key=f"file_type_select_{chat_username}"
    )

    uploaded_file = None  # default

    # Step 2: Conditional uploader based on selected type
    if file_type == "Image":
        uploaded_file = st.file_uploader(
            "📷 Upload Image",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            key=f"file_upload_image_{chat_username}",
            help="Upload an image file"
        )

    elif file_type == "Video":
        uploaded_file = st.file_uploader(
            "🎥 Upload Video",
            type=['mp4', 'avi', 'mov', 'mkv'],
            key=f"file_upload_video_{chat_username}",
            help="Upload a video file"
        )

    elif file_type == "Audio":
        uploaded_file = st.file_uploader(
            "🎵 Upload Audio",
            type=['mp3', 'wav', 'ogg', 'm4a'],
            key=f"file_upload_audio_{chat_username}",
            help="Upload an audio file"
        )

    elif file_type == "Document":
        uploaded_file = st.file_uploader(
            "📄 Upload Document",
            type=['pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls'],
            key=f"file_upload_document_{chat_username}",
            help="Upload a document file"
        )

    # Step 3: Keep track of file type for later use
    st.session_state[f"uploaded_file_type_{chat_username}"] = file_type
    st.session_state[f"uploaded_file_{chat_username}"] = uploaded_file


    # Send button
    def clear_input_field(key: str):
        if key in st.session_state:
            st.session_state[key] = ""


    col_send, col_clear = st.columns([4, 1])

    with col_send:
        st.button(
        "📤 Send Message",
        key=f"send_button_{chat_username}",
        on_click=send_message,
        args=(
            chat_username,
            current_user_id,
            other_user_id,
            message_text,
            uploaded_file,   # ✅ single uploaded file
            file_type        # ✅ dropdown selection
        ),
        use_container_width=True
    )

    with col_clear:
        st.button(
            "🗑️ Clear",
            key=f"clear_button_{chat_username}",
            on_click=clear_input_field,
            args=(f"message_input_{chat_username}",),
            use_container_width=True
        )


def display_message(message, current_username):
    """Display a single message in the chat"""
    # message is a dict with: sender_username, receiver_username, message_content, created_at
    sender_username = message.get('sender_username', '')
    message_content = message.get('message', '')
    timestamp = message.get('created_at', '')
    
    # Convert timestamp if it's a datetime object
    if isinstance(timestamp, datetime):
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    elif timestamp:
        timestamp = str(timestamp)
    
    is_own = sender_username == current_username
    
    # Escape HTML in message content for security
    import html
    safe_content = html.escape(str(message_content))
    
    if is_own:
        st.markdown(
            f"""
            <div style="
                background-color: #007bff;
                color: white;
                padding: 10px;
                border-radius: 10px;
                margin: 5px 0;
                margin-left: 20%;
                text-align: right;
            ">
                <strong>You</strong><br>
                {safe_content}
                <br><small style="opacity: 0.8;">{timestamp}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                background-color: #e9ecef;
                color: black;
                padding: 10px;
                border-radius: 10px;
                margin: 5px 0;
                margin-right: 20%;
            ">
                <strong>{sender_username}</strong><br>
                {safe_content}
                <br><small style="opacity: 0.6;">{timestamp}</small>
            </div>
            """,
            unsafe_allow_html=True
        )


def send_message(chat_username, sender_id, receiver_id, message_text, uploaded_file, file_type):
    """Handle sending a message to the database"""
    
    # Check if there's any content to send
    has_content = False
    message_parts = []
    
    if message_text and message_text.strip():
        has_content = True
        message_parts.append(message_text.strip())
    
    if uploaded_file is not None and file_type != "None":
        has_content = True
        file_info = f"{uploaded_file.name} ({uploaded_file.size} bytes)"
        message_parts.append(f"📎 {file_type}: {file_info}")
    
    if not has_content:
        st.warning("Please enter a message or upload a file!")
        return
    
    # Combine all message parts
    full_message = '\n'.join(message_parts)
    
    # Convert message to bytes for blob storage
    message_bytes = full_message.encode('utf-8')

    if uploaded_file is not None:
        file_data = uploaded_file.read()

        # Determine file column based on type
        file_column = None
        if file_type == "Image":
            file_column = "image"
        elif file_type == "Video":
            file_column = "video"
        elif file_type == "Audio":
            file_column = "audio"
        elif file_type == "Document":
            file_column = "document"

        if file_column:
            conn.run_query(
                f"INSERT INTO file ({file_column}) VALUES (%s);",
                (file_data,),
                fetch=False
            )
    
    # Save to database
    success = conn.run_query(
        "INSERT INTO text (message, sender_id, receiver_id) VALUES (%s, %s, %s);",
        (message_bytes, sender_id, receiver_id),
        fetch=False
    )
    
    if success:
        # Clear inputs
        st.session_state[f"message_input_{chat_username}"] = ""
        st.success("Message sent!")
    else:
        st.error("Failed to send message. Please try again.")


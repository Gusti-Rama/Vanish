import streamlit as st
import koneksi as conn
import pandas as pd
from fungsi import file_encrypt 
from page.chat import get_user_id 
from fungsi import db_encrypt

def file_page():    
    current_username = st.session_state.get('username')
    if not current_username:
        st.error("Silakan login terlebih dahulu!")
        return
    
    current_user_id = get_user_id(current_username)
    if not current_user_id:
        st.error("User tidak ditemukan di database!")
        return

    st.title("🔒 File Terenkripsi")
    st.info("Kirim dan terima file rahasia menggunakan enkripsi Blowfish. Kunci dekripsi harus Anda bagikan dengan penerima secara terpisah (misalnya, melalui chat).")

    tab1, tab2 = st.tabs(["📤 Kirim File", "📥 File Masuk"])

    with tab1:
        st.header("Kirim File Aman")
        
        try:
            # Kita masih perlu daftar user buat validasi
            users_df = conn.run_query(
                "SELECT id_user, username FROM user WHERE id_user != %s",
                (current_user_id,),
                fetch=True
            )
            if users_df is None or users_df.empty:
                st.warning("Tidak ada pengguna lain untuk dikirimi file.")
                return
            
            # user_list buat nyari ID nanti
            user_list = users_df.set_index('id_user')['username'].to_dict()
            
            receiver_username_input = st.text_input(
                "Pilih Penerima:",
                placeholder="Masukkan username penerima..."
            )

            uploaded_file = st.file_uploader("Pilih file yang akan dienkripsi:")
            st.info("Batas ukuran file 16MB")
            
            encryption_key = st.text_input(
                "Buat Kunci Enkripsi (Password):", 
                type="password", 
                key="enc_key",
                help="Panjang kunci minimal 4 karakter." 
            )

            if st.button("Enkripsi & Kirim File", use_container_width=True):
                
                receiver_username = receiver_username_input.strip()
                receiver_id = next((uid for uid, uname in user_list.items() if uname == receiver_username), None)

                if receiver_id and uploaded_file and encryption_key:
                    
                    if len(encryption_key.encode('utf-8')) < 4:
                        st.error("Kunci Enkripsi terlalu pendek! Harap gunakan minimal 4 karakter.")
                    else:
                        with st.spinner("Membaca file dan mengenkripsi..."):
                            try:
                                file_bytes = uploaded_file.getvalue()
                                # blowfish
                                encrypted_blowfish_bytes = file_encrypt.encrypt_bytes(file_bytes, encryption_key)
                                
                                # enkrip DB (Chacha20)
                                encrypted_db_payload = db_encrypt.encrypt_db_data(encrypted_blowfish_bytes)
                                encrypted_file_name = db_encrypt.encrypt_db_string(uploaded_file.name)
                                encrypted_file_type = db_encrypt.encrypt_db_string(uploaded_file.type)
                                category = "file"
                                
                                success = conn.run_query(
                                    """
                                    INSERT INTO file (file_data, file_name, file_type, sender_id, receiver_id, category) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    """,
                                    (
                                        encrypted_db_payload, 
                                        encrypted_file_name, 
                                        encrypted_file_type, 
                                        current_user_id, 
                                        receiver_id,
                                        category
                                    ),
                                    fetch=False
                                )
                                
                                if success:
                                    st.success(f"Berhasil! File terenkripsi telah dikirim ke {receiver_username}.")
                                   
                                    original_name = uploaded_file.name
                                    original_mime = uploaded_file.type

                                    st.download_button(
                                        label=f"Download File Terenkripsi ({original_name})",
                                        data=encrypted_blowfish_bytes,
                                        file_name=original_name,
                                        mime=original_mime,     
                                        use_container_width=True
                                    )
                                 
                                    
                                else:
                                    st.error("Gagal menyimpan file ke database.")
                            except Exception as e:
                                st.error(f"Terjadi kesalahan saat enkripsi: {e}")
                else:
                    if not receiver_id:
                        st.error(f"Username '{receiver_username}' tidak ditemukan atau Anda belum mengisi nama penerima.")
                    elif not uploaded_file:
                        st.warning("Harap pilih file.")
                    elif not encryption_key:
                        st.warning("Harap masukkan kunci enkripsi.")
            
        except Exception as e:
            st.error(f"Gagal memuat daftar pengguna: {e}")

    with tab2:
        st.header("File Diterima")
        
        try:
            files_df = conn.run_query(
                """
                SELECT f.id_file, f.file_name, f.file_type, f.uploaded_at, u.username as sender_username 
                FROM file f 
                JOIN user u ON f.sender_id = u.id_user 
                WHERE f.receiver_id = %s AND f.category = 'file'
                ORDER BY f.uploaded_at DESC
                """,
                (current_user_id,),
                fetch=True
            )
            
            if files_df is None:
                st.error("Gagal mengambil data file.")
            elif files_df.empty:
                st.info("Tidak ada file yang diterima.")
            else:
                st.info(f"Anda memiliki {len(files_df)} file.")
                
                for _, row in files_df.iterrows():
                    file_id = row['id_file']
                    
                    try:
                        decrypted_file_name = db_encrypt.decrypt_db_string(row['file_name'])
                        decrypted_file_type = db_encrypt.decrypt_db_string(row['file_type'])
                    except Exception as e:
                        st.error(f"Gagal mendekripsi metadata file {file_id}. Data korup atau kunci DB salah.")
                        continue

                    with st.expander(f"🔒 **{decrypted_file_name}** dari **{row['sender_username']}**"):
                        st.caption(f"Diterima: {row['uploaded_at']} | Tipe: {decrypted_file_type}")
                        
                        decryption_key = st.text_input(
                            "Masukkan Kunci Dekripsi (Blowfish):", 
                            type="password", 
                            key=f"dec_key_{file_id}",
                            help="Panjang kunci minimal 4 karakter." 
                        )
                        
                        if st.button("Dekripsi & Download", key=f"btn_dec_{file_id}", use_container_width=True):
                            if decryption_key:
                                
                                if len(decryption_key.encode('utf-8')) < 4:
                                    st.error("Kunci Dekripsi terlalu pendek! Harap gunakan minimal 4 karakter.")
                                else:
                                    with st.spinner("Mengambil file dan mendekripsi..."):
                                        try:
                                            file_data_df = conn.run_query(
                                                "SELECT file_data FROM file WHERE id_file = %s",
                                                (file_id,),
                                                fetch=True
                                            )
                                            
                                            if not file_data_df.empty:
                                                encrypted_db_payload = file_data_df.iloc[0]['file_data']
                                                encrypted_blowfish_bytes = db_encrypt.decrypt_db_data(encrypted_db_payload)
                                                decrypted_bytes = file_encrypt.decrypt_bytes(encrypted_blowfish_bytes, decryption_key)
                                                
                                                st.success("Dekripsi berhasil!")
                                                st.download_button(
                                                    label=f"Download '{decrypted_file_name}'",
                                                    data=decrypted_bytes,
                                                    file_name=decrypted_file_name,
                                                    mime=decrypted_file_type,
                                                    use_container_width=True
                                                )
                                            else:
                                                st.error("Tidak dapat menemukan data file.")
                                        except Exception as e:
                                            st.error(f"Gagal mendekripsi! Kunci Blowfish salah atau file korup.")
                            else:
                                st.warning("Masukkan kunci dekripsi terlebih dahulu.")

        except Exception as e:
            st.error(f"Gagal memuat file masuk: {e}")
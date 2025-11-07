import streamlit as st
from PIL import Image
from fungsi import steganography
import io
import koneksi as conn
from page.chat import get_user_id 
from fungsi import db_encrypt 

def stego_page():  
    current_username = st.session_state.get('username')
    if not current_username:
        st.error("Silahkan login terlebih dahulu!")
        return
    
    current_user_id = get_user_id(current_username)
    if not current_user_id:
        st.error("User tidak ditemukan di database!")
        return
    
    st.title("🖼️ Steganografi")
    st.info("Kirim dan terima gambar yang berisi pesan rahasia (teks atau gambar lain). Pesan hanya bisa diekstrak jika penerima tahu 'Threshold' yang Anda gunakan.")

    with st.expander("⚙️ Pengaturan (Adaptive LSB)"):
        st.markdown("Pastikan pengirim dan penerima menggunakan **Threshold** yang SAMA PERSIS.")
        threshold_percentile = st.slider(
            "Threshold Kompleksitas (Persentil)",
            min_value=1,
            max_value=99,
            value=60,
            key="stego_threshold",
            help="Nilai ini bertindak sebagai 'kunci'. Penerima harus memasukkan nilai yang sama."
        )
        st.info(f"Pengaturan saat ini: **{100 - threshold_percentile}%** area gambar terkompleks akan digunakan.")

    tab_text, tab_image, tab_inbox = st.tabs([
        "🖼️ Kirim Teks-dalam-Gambar", 
        "🖼️+🖼️ Kirim Gambar-dalam-Gambar", 
        "📥 Steganography-Image Masuk"
    ])

    with tab_text:
        st.header("Sembunyikan Pesan Teks & Kirim")
        
        try:
            users_df = conn.run_query(
                "SELECT id_user, username FROM user WHERE id_user != %s",
                (current_user_id,),
                fetch=True
            )
            if users_df is None or users_df.empty:
                st.warning("Tidak ada pengguna lain untuk dikirimi file.")
            else:
                # Dekripsi username untuk ditampilkan
                decrypted_user_list = {}
                for _, row in users_df.iterrows():
                    try:
                        decrypted_name = db_encrypt.decrypt_db_string(row['username'])
                        decrypted_user_list[row['id_user']] = decrypted_name
                    except Exception: 
                        pass # Abaikan user yang gagal didekrip
                
                user_list = decrypted_user_list
                
                receiver_username_input = st.text_input(
                    "1. Pilih Penerima:",
                    key="stego_text_receiver",
                    placeholder="Masukkan username penerima..."
                )

                cover_image_file = st.file_uploader(
                    "2. Upload Gambar Sampul (Cover Image):", 
                    type=['png', 'jpg', 'jpeg', 'bmp'],
                    key="stego_text_enc_upload"
                )
                
                secret_message = st.text_area(
                    "3. Masukkan Pesan Rahasia (Teks):",
                    key="stego_text_enc_text",
                    height=150
                )
            
                if st.button("Sembunyikan Teks & Kirim", key="stego_text_enc_btn", use_container_width=True):
                    
                    receiver_username = receiver_username_input.strip()
                    receiver_id = next((uid for uid, uname in user_list.items() if uname == receiver_username), None)

                    if receiver_id and cover_image_file and secret_message:
                        with st.spinner("Membuat Steganography-image (teks) dan mengirim..."):
                            try:
                                image = Image.open(cover_image_file)
                                with io.BytesIO() as output:
                                    image.save(output, format="PNG")
                                    png_data = output.getvalue()
                                image_lossless = Image.open(io.BytesIO(png_data))

                                stego_image = steganography.embed_msg(image_lossless, secret_message, threshold_percentile)
                                
                                buf = io.BytesIO()
                                stego_image.save(buf, format="PNG")
                                byte_im = buf.getvalue() 

                                secret_file_name = f"pesan_teks_dari_{current_username}.txt"
                                secret_file_type = "text/plain"
                                category = "stego_text" 
                                
                                encrypted_db_payload = db_encrypt.encrypt_db_data(byte_im)
                                encrypted_file_name = db_encrypt.encrypt_db_string(secret_file_name) 
                                encrypted_file_type = db_encrypt.encrypt_db_string(secret_file_type) 

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
                                    st.success(f"Berhasil! Steganography-Image (teks) telah dikirim ke {receiver_username}.")
                                    stego_container_name = f"Steganograpy_TXT_from_{current_username}_{cover_image_file.name}"
                                    st.download_button(
                                        label=f"Download Salinan '{stego_container_name}'",
                                        data=byte_im,
                                        file_name=stego_container_name,
                                        mime="image/png",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("Gagal menyimpan file ke database.")
                            except ValueError as e:
                                st.error(f"{e}")
                            except Exception as e:
                                st.error(f"Terjadi kesalahan: {e}")
                    else:
                        if receiver_username == current_username:
                            st.error("Anda tidak dapat mengirim file ke diri sendiri.")
                        elif not receiver_id:
                            st.error(f"Username '{receiver_username}' tidak ditemukan atau Anda belum mengisi nama penerima.")
                        elif not cover_image_file:
                            st.warning("Harap pilih gambar sampul.")
                        elif not secret_message:
                            st.warning("Harap masukkan pesan teks rahasia.")
            
        except Exception as e:
            st.error(f"Gagal memuat daftar pengguna: {e}")

    with tab_image:
        st.header("Sembunyikan Gambar & Kirim")
        
        try:
            users_df_img = conn.run_query(
                "SELECT id_user, username FROM user WHERE id_user != %s",
                (current_user_id,),
                fetch=True
            )
            if users_df_img is None or users_df_img.empty:
                st.warning("Tidak ada pengguna lain untuk dikirimi file.")
            else:
                # Dekripsi username untuk ditampilkan
                decrypted_user_list_img = {}
                for _, row in users_df_img.iterrows():
                    try:
                        decrypted_name = db_encrypt.decrypt_db_string(row['username'])
                        decrypted_user_list_img[row['id_user']] = decrypted_name
                    except Exception: 
                        pass # Abaikan user yang gagal didekrip
                
                user_list_img = decrypted_user_list_img
                
                receiver_username_input_img = st.text_input(
                    "1. Pilih Penerima:",
                    key="stego_img_receiver",
                    placeholder="Masukkan username penerima..."
                )

                cover_image_file_img = st.file_uploader(
                    "2. Upload Gambar Sampul (Cover Image):", 
                    type=['png', 'jpg', 'jpeg', 'bmp'],
                    key="stego_img_enc_upload_cover"
                )
                
                secret_image_file_img = st.file_uploader(
                    "3. Upload Gambar Rahasia (Yang akan disembunyikan):", 
                    type=['png', 'jpg', 'jpeg', 'bmp'],
                    key="stego_img_enc_upload_secret"
                )
            
                if st.button("Sembunyikan Gambar & Kirim", key="stego_img_enc_btn", use_container_width=True):
                    
                    receiver_username_img = receiver_username_input_img.strip()
                    receiver_id_img = next((uid for uid, uname in user_list_img.items() if uname == receiver_username_img), None)
                    
                    if receiver_id_img and cover_image_file_img and secret_image_file_img:
                        with st.spinner("Membuat Steganography-image (gambar) dan mengirim..."):
                            try:
                                image_cover = Image.open(cover_image_file_img)
                                secret_bytes = secret_image_file_img.getvalue()
                                
                                with io.BytesIO() as output:
                                    image_cover.save(output, format="PNG")
                                    png_data = output.getvalue()
                                image_lossless = Image.open(io.BytesIO(png_data))

                                stego_image = steganography.embed_bytes(image_lossless, secret_bytes, threshold_percentile)
                                
                                buf = io.BytesIO()
                                stego_image.save(buf, format="PNG")
                                byte_im = buf.getvalue() 

                                secret_file_name = secret_image_file_img.name
                                secret_file_type = secret_image_file_img.type
                                category = "stego_image" 
                                
                                encrypted_db_payload = db_encrypt.encrypt_db_data(byte_im)
                                encrypted_file_name = db_encrypt.encrypt_db_string(secret_file_name)
                                encrypted_file_type = db_encrypt.encrypt_db_string(secret_file_type) 
                                
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
                                        receiver_id_img,
                                        category
                                    ),
                                    fetch=False
                                )
                                
                                if success:
                                    st.success(f"Berhasil! Steganography-Image (gambar) telah dikirim ke {receiver_username_img}.")
                                    stego_container_name = f"Steganography_IMG_from_{current_username}_{cover_image_file_img.name}"
                                    st.download_button(
                                        label=f"Download Salinan '{stego_container_name}'",
                                        data=byte_im,
                                        file_name=stego_container_name,
                                        mime="image/png",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("Gagal menyimpan file ke database.")
                            except ValueError as e:
                                st.error(f"{e}")
                            except Exception as e:
                                st.error(f"Terjadi kesalahan: {e}")
                    else:
                        if receiver_username_img == current_username:
                            st.error("Anda tidak dapat mengirim file ke diri sendiri.")
                        elif not receiver_id_img:
                            st.error(f"Username '{receiver_username_img}' tidak ditemukan atau Anda belum mengisi nama penerima.")
                        elif not cover_image_file_img:
                            st.warning("Harap pilih gambar sampul.")
                        elif not secret_image_file_img:
                            st.warning("Harap pilih gambar rahasia.")
            
        except Exception as e:
            st.error(f"Gagal memuat daftar pengguna: {e}")

    with tab_inbox:
        st.header("Steganography-Image Masuk")
        st.warning("Pastikan 'Pengaturan Lanjutan' di atas SAMA PERSIS dengan yang digunakan pengirim.")

        try:
            files_df = conn.run_query(
                """
                SELECT f.id_file, f.file_name, f.file_type, f.uploaded_at, u.username as sender_username, f.category
                FROM file f 
                JOIN user u ON f.sender_id = u.id_user 
                WHERE f.receiver_id = %s AND (f.category = 'stego_text' OR f.category = 'stego_image')
                ORDER BY f.uploaded_at DESC
                """,
                (current_user_id,),
                fetch=True
            )
            
            if files_df is None:
                st.error("Gagal mengambil data file.")
            elif files_df.empty:
                st.info("Tidak ada Steganography-image yang diterima.")
            else:
                st.info(f"Anda memiliki {len(files_df)} Steganography-image.")
                
                for _, row in files_df.iterrows():
                    file_id = row['id_file']
                    category = row['category']
                    
                    try:
                        decrypted_sender_username = db_encrypt.decrypt_db_string(row['sender_username'])
                    except Exception as e:
                        decrypted_sender_username = "[Pengirim Gagal Dekrip]"

                    try:
                        decrypted_file_name = db_encrypt.decrypt_db_string(row['file_name'])
                        decrypted_file_type = db_encrypt.decrypt_db_string(row['file_type'])
                    except Exception as e:
                        st.error(f"Gagal mendekripsi metadata file {file_id}. Data korup atau kunci DB salah.")
                        continue

                    msg_type_display = "Teks Tersembunyi" if category == 'stego_text' else "Gambar Tersembunyi"

                    with st.expander(f"🖼️ **{decrypted_file_name}** dari **{decrypted_sender_username}**"):
                        st.caption(f"Tipe Pesan: {msg_type_display} | Diterima: {row['uploaded_at']}")
                        
                        if category == 'stego_text':
                            if st.button("Ekstrak Pesan Teks", key=f"btn_dec_txt_{file_id}", use_container_width=True):
                                with st.spinner("Mengambil gambar dan mencari pesan teks..."):
                                    try:
                                        file_data_df = conn.run_query(
                                            "SELECT file_data FROM file WHERE id_file = %s",
                                            (file_id,),
                                            fetch=True
                                        )
                                        
                                        if not file_data_df.empty:
                                            encrypted_db_payload = file_data_df.iloc[0]['file_data']
                                            image_bytes = db_encrypt.decrypt_db_data(encrypted_db_payload)
                                            image = Image.open(io.BytesIO(image_bytes))
                                            extracted_message = steganography.extract_msg(image, threshold_percentile)
                                            
                                            if extracted_message:
                                                st.success("Pesan rahasia berhasil ditemukan!")
                                                st.text_area("Pesan:", value=extracted_message, height=150, disabled=True, key=f"txt_area_{file_id}")
                                            else:
                                                st.warning("Tidak ada pesan teks yang ditemukan. (Pastikan 'Pengaturan Lanjutan' Anda benar).")
                                        else:
                                            st.error("Tidak dapat menemukan data file.")
                                    except Exception as e:
                                        st.error(f"Gagal mengekstrak! Kunci DB salah, data korup, atau threshold salah. Error: {e}")
                        
                        elif category == 'stego_image':
                            if st.button("Ekstrak Gambar Tersembunyi", key=f"btn_dec_img_{file_id}", use_container_width=True):
                                with st.spinner("Mengambil gambar dan mencari gambar tersembunyi..."):
                                    try:
                                        file_data_df = conn.run_query(
                                            "SELECT file_data FROM file WHERE id_file = %s",
                                            (file_id,),
                                            fetch=True
                                        )
                                        
                                        if not file_data_df.empty:
                                            encrypted_db_payload = file_data_df.iloc[0]['file_data']
                                            image_bytes = db_encrypt.decrypt_db_data(encrypted_db_payload)
                                            image = Image.open(io.BytesIO(image_bytes))
                                            extracted_image_bytes = steganography.extract_bytes(image, threshold_percentile)
                                            
                                            if extracted_image_bytes:
                                                st.success("Gambar rahasia berhasil diekstrak!")
                                                st.image(extracted_image_bytes, caption=f"Gambar diekstrak: {decrypted_file_name}")
                                                
                                                st.download_button(
                                                    label=f"Download Gambar Tersembunyi '{decrypted_file_name}'",
                                                    data=extracted_image_bytes,
                                                    file_name=decrypted_file_name,
                                                    mime=decrypted_file_type,
                                                    use_container_width=True,
                                                    key=f"download_img_{file_id}"
                                                )
                                            else:
                                                st.warning("Tidak ada gambar tersembunyi yang ditemukan. (Pastikan 'Pengaturan Lanjutan' Anda benar).")
                                        else:
                                            st.error("Tidak dapat menemukan data file.")
                                    except Exception as e:
                                        st.error(f"Gagal mengekstrak! Kunci DB salah, data korup, atau threshold salah. Error: {e}")

        except Exception as e:
            st.error(f"Gagal memuat file masuk: {e}")
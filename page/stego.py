import streamlit as st
from PIL import Image
from fungsi import steganography
import io
import koneksi as conn
from page.chat import get_user_id 
from fungsi import db_encrypt # --- PERUBAHAN BARU ---

def stego_page():
    """
    Menampilkan halaman untuk MENGIRIM dan MENERIMA stego-image
    melalui database.
    """
    
    current_username = st.session_state.get('username')
    if not current_username:
        st.error("Silakan login terlebih dahulu!")
        return
    
    current_user_id = get_user_id(current_username)
    if not current_user_id:
        st.error("User tidak ditemukan di database!")
        return
    
    st.title("🖼️ Brankas Steganografi")
    st.info("Kirim dan terima gambar yang berisi pesan rahasia. Pesan hanya bisa diekstrak jika penerima tahu 'Threshold' yang Anda gunakan.")

    with st.expander("⚙️ Pengaturan Lanjutan (Adaptive LSB)"):
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

    tab1, tab2 = st.tabs(["🖼️ Kirim Stego-Image", "📥 Stego-Image Masuk"])

    with tab1:
        st.header("Sembunyikan Pesan & Kirim")
        
        try:
            users_df = conn.run_query(
                "SELECT id_user, username FROM user WHERE id_user != %s",
                (current_user_id,),
                fetch=True
            )
            if users_df is None or users_df.empty:
                st.warning("Tidak ada pengguna lain untuk dikirimi file.")
                return
            
            user_list = users_df.set_index('id_user')['username'].to_dict()
            
            receiver_username = st.selectbox(
                "1. Pilih Penerima:",
                options=user_list.values(),
                key="stego_receiver"
            )
            receiver_id = next((uid for uid, uname in user_list.items() if uname == receiver_username), None)

            cover_image_file = st.file_uploader(
                "2. Upload Gambar Sampul (Cover Image):", 
                type=['png', 'jpg', 'jpeg', 'bmp'],
                key="stego_enc_upload"
            )
            
            secret_message = st.text_area(
                "3. Masukkan Pesan Rahasia:",
                key="stego_enc_text",
                height=150
            )
        
            if st.button("Sembunyikan Pesan & Kirim", key="stego_enc_btn", use_container_width=True):
                if receiver_id and cover_image_file and secret_message:
                    with st.spinner("Membuat stego-image dan mengirim..."):
                        try:
                            image = Image.open(cover_image_file)
                            with io.BytesIO() as output:
                                image.save(output, format="PNG")
                                png_data = output.getvalue()
                            image_lossless = Image.open(io.BytesIO(png_data))

                            # 1. Buat Stego Image (App-level)
                            stego_image = steganography.embed_msg(image_lossless, secret_message, threshold_percentile)
                            
                            buf = io.BytesIO()
                            stego_image.save(buf, format="PNG")
                            byte_im = buf.getvalue() # Bytes Stego Image

                            file_name_db = f"stego_from_{current_username}_{cover_image_file.name}.png"
                            
                            # --- PERUBAHAN BARU ---
                            # 2. Enkripsi ChaCha20 (DB-level)
                            encrypted_db_payload = db_encrypt.encrypt_db_data(byte_im)
                            encrypted_file_name = db_encrypt.encrypt_db_string(file_name_db)
                            encrypted_file_type = db_encrypt.encrypt_db_string("image/png")
                            category = "stego"
                            # --- AKHIR PERUBAHAN ---

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
                                st.success(f"Berhasil! Stego-Image telah dikirim ke {receiver_username}.")
                            
                                # Download salinan Stego-Image (bukan yang dienkripsi DB)
                                st.download_button(
                                    label=f"Download Salinan '{file_name_db}'",
                                    data=byte_im,
                                    file_name=file_name_db,
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
                    st.warning("Harap pilih Penerima, Gambar, dan masukkan Pesan.")
            
        except Exception as e:
            st.error(f"Gagal memuat daftar pengguna: {e}")

    with tab2:
        st.header("Stego-Image Masuk")
        st.warning("Pastikan 'Pengaturan Lanjutan' di atas SAMA PERSIS dengan yang digunakan pengirim.")

        try:
            # --- PERUBAHAN BARU: Query berdasarkan category ---
            files_df = conn.run_query(
                """
                SELECT f.id_file, f.file_name, f.file_type, f.uploaded_at, u.username as sender_username 
                FROM file f 
                JOIN user u ON f.sender_id = u.id_user 
                WHERE f.receiver_id = %s AND f.category = 'stego'
                ORDER BY f.uploaded_at DESC
                """,
                (current_user_id,),
                fetch=True
            )
            # --- AKHIR PERUBAHAN ---
            
            if files_df is None:
                st.error("Gagal mengambil data file.")
            elif files_df.empty:
                st.info("Tidak ada stego-image yang diterima.")
            else:
                st.info(f"Anda memiliki {len(files_df)} stego-image.")
                
                for _, row in files_df.iterrows():
                    file_id = row['id_file']
                    
                    # --- PERUBAHAN BARU: Dekripsi file_name & file_type ---
                    try:
                        decrypted_file_name = db_encrypt.decrypt_db_string(row['file_name'])
                        decrypted_file_type = db_encrypt.decrypt_db_string(row['file_type'])
                    except Exception as e:
                        st.error(f"Gagal mendekripsi metadata file {file_id}. Data korup atau kunci DB salah.")
                        continue
                    # --- AKHIR PERUBAHAN ---

                    with st.expander(f"🖼️ **{decrypted_file_name}** dari **{row['sender_username']}**"):
                        st.caption(f"Diterima: {row['uploaded_at']} | Tipe: {decrypted_file_type}")
                        
                        if st.button("Ekstrak Pesan", key=f"btn_dec_{file_id}", use_container_width=True):
                            with st.spinner("Mengambil gambar dan mencari pesan..."):
                                try:
                                    file_data_df = conn.run_query(
                                        "SELECT file_data FROM file WHERE id_file = %s",
                                        (file_id,),
                                        fetch=True
                                    )
                                    
                                    if not file_data_df.empty:
                                        # 1. Ambil payload terenkripsi ChaCha20 dari DB
                                        encrypted_db_payload = file_data_df.iloc[0]['file_data']
                                        # 2. Dekripsi ChaCha20 (DB-level)
                                        image_bytes = db_encrypt.decrypt_db_data(encrypted_db_payload)
                                        
                                        # 3. Konversi bytes kembali ke PIL Image
                                        image = Image.open(io.BytesIO(image_bytes))
                                        
                                        # 4. Ekstrak pesan menggunakan threshold dari slider
                                        extracted_message = steganography.extract_msg(image, threshold_percentile)
                                        
                                        if extracted_message:
                                            st.success("Pesan rahasia berhasil ditemukan!")
                                            st.text_area("Pesan:", value=extracted_message, height=150, disabled=True)
                                            
                                            st.download_button(
                                                label=f"Download Gambar Asli '{decrypted_file_name}'",
                                                data=image_bytes,
                                                file_name=decrypted_file_name,
                                                mime=decrypted_file_type,
                                                use_container_width=True
                                            )
                                           
                                        else:
                                            st.warning("Tidak ada pesan rahasia yang ditemukan. (Pastikan 'Pengaturan Lanjutan' Anda benar).")
                                    else:
                                        st.error("Tidak dapat menemukan data file.")
                                except Exception as e:
                                    st.error(f"Gagal mengekstrak! Kunci DB salah, data korup, atau threshold salah. Error: {e}")

        except Exception as e:
            st.error(f"Gagal memuat file masuk: {e}")
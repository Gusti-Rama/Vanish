import streamlit as st
import koneksi as conn

def home():
    st.title("🏠 Selamat Datang di Vanish")
    st.markdown("Pilih opsi di sidebar kiri dan tambahkan obrolan baru untuk memulai.")    
    st.divider()
    with st.container(border=True):
        st.subheader("🔒 Bagaimana Obrolan Aman Ini Bekerja?")
        st.markdown(
            """
            Vanish dirancang untuk privasi absolut. Semua pesan Anda diamankan menggunakan **Enkripsi Berlapis (Super-Enkripsi)** sebelum pernah meninggalkan komputer Anda.
            """
        )
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 1. Ditulis (Plaintext)")
            st.markdown("Anda menulis pesan seperti biasa.")
        with c2:
            st.markdown("#### 2. Dienkripsi (Super-Enkripsi)")
            st.markdown("Pesan dienkripsi dengan **Caesar**, lalu **XOR**, lalu **RSA**.")
        with c3:
            st.markdown("#### 3. Dikirim (Ciphertext)")
            st.markdown("Hanya teks acak (ciphertext) yang disimpan di database dan dikirim ke penerima.")
        
        st.markdown("---") 
        st.markdown("#### 📖 Cara Mengirim dan Membaca Pesan Chat")
        st.markdown(
            """
            Karena faktor keamanan, Anda **tidak bisa** langsung membaca pesan dari kotak obrolan. Anda harus menyetujui kunci **Caesar** dan **XOR** dengan penerima terlebih dahulu.
            * **Untuk Mengirim Pesan:**
                1.  Buka 'Chat'.
                2.  Tulis pesan seperti biasa
                3.  Pilih **Kunci (Shift & XOR)** yang telah disetujui oleh Penerima.
                4.  Klik 'Kirim'. Pesan akan otomatis terenkripsi dan dikirim sebagai ciphertext ke penerima.
            * **Untuk Membaca Pesan:**
                1.  Salin (Copy) pesan ciphertext yang Anda terima dari chat.
                2.  Buka halaman 'Demo Super-Enkripsi'.
                3.  Tempel (Paste) ke tab **'Proses Dekripsi'**.
                4.  Pilih **Kunci (Shift & XOR)** yang telah disetujui dengan Pengirim.
                5.  Klik 'Dekripsi' untuk melihat pesan asli.
            """
        )
        st.warning(
            "**PENTING:** Anda dan penerima harus menyetujui dan menggunakan **Kunci Caesar & XOR** yang sama persis agar pesan bisa dibaca!",
            icon="🔑"
        )

    st.divider()

    with st.container(border=True):
        st.subheader("🔒 Kirim File Terenkripsi")
        st.markdown(
            """
            Fitur ini memungkinkan Anda mengirim file apa pun (dokumen, gambar, ,video, audio, .zip, dll.) dengan size max 16MB dalam format yang terenkripsi penuh. 
            Algoritma yang digunakan adalah **Blowfish**, sebuah *block cipher* simetris yang cepat dan aman.
            """
        )
        st.markdown("---") 
        st.markdown("#### 📖 Cara Mengirim dan Menerima File")
        st.markdown(
            """
            Sama seperti chat, enkripsi file menggunakan **Kunci (Password)** yang harus Anda setujui dengan penerima.
            * **Untuk Mengirim File:**
                1.  Buka halaman 'File Encryption'.
                2.  Di tab 'Kirim File', pilih Penerima.
                3.  Upload file yang ingin Anda kirim.
                4.  Buat **Kunci Enkripsi (Password)** (minimal 4 karakter).
                5.  Klik 'Enkripsi & Kirim File'.
            * **Untuk Menerima File:**
                1.  Buka halaman 'File Encryption' -> tab 'File Masuk'.
                2.  Temukan file yang ingin Anda buka di dalam *expander*.
                3.  Masukkan **Kunci Dekripsi (Password)** yang diberikan oleh pengirim.
                4.  Klik 'Dekripsi & Download'.
            """
        )
        st.warning(
            "**PENTING:** Anda dan penerima harus menyetujui dan menggunakan **Kunci (Password)** yang sama persis agar file bisa dibuka!",
            icon="🔐"
        )
    st.divider()

    with st.container(border=True):
        st.subheader("🖼️ Steganography")
        st.markdown(
            """
            Steganografi adalah seni menyembunyikan data rahasia *di dalam* data lain yang tidak berbahaya (dalam kasus ini, gambar). 
            Metode ini menggunakan **Adaptive LSB (Least Significant Bit)**, yang secara cerdas menyisipkan data (teks maupun gambar lain) hanya di area "kompleks" pada gambar sampul agar tidak mudah terdeteksi.
            """
        )
        st.markdown("---") 
        st.markdown("#### 📖 Kunci & Cara Penggunaan")
        st.markdown(
            """
            Sama seperti sebelumnya, steganography menggunakan nilai **Threshold** yang harus Anda setujui dengan penerima.

            * **Untuk Menyembunyikan (Teks atau Gambar):**
                1.  Buka halaman 'Steganography'.
                2.  Tentukan **Threshold** di 'Pengaturan Lanjutan' yang telah disetujui dengan Penerima.
                3.  Pilih tab 'Kirim Teks' atau 'Kirim Gambar'.
                4.  Pilih Penerima, upload Gambar Sampul, dan data rahasia (teks/gambar).
                5.  Klik 'Sembunyikan & Kirim'.
            * **Untuk Mengekstrak (Teks atau Gambar):**
                1.  Buka halaman 'Steganography'.
                2.  Tentukan **Threshold** yang telah disetujui dengan Pengirim.
                3.  Pilih tab 'Teks Masuk' atau 'Gambar Masuk'.
                4.  Temukan file kiriman dan klik 'Ekstrak'.
            """
        )
        st.warning(
            "**PENTING:** Anda dan penerima harus menyetujui dan menggunakan nilai **Threshold** yang sama persis agar data rahasia dapat diekstrak!",
            icon="🎨"
        )
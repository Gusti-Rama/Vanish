import streamlit as st
from fungsi import caesar, xor, rsa

def demo_page():
    st.title("🧪 Demo Proses Super-Enkripsi")
    st.info("Gunakan alat ini untuk mendekripsi pesan yang Anda terima dari chat.")

    # Inisialisasi session_state untuk menyimpan hasil
    if "demo_enc_results" not in st.session_state:
        st.session_state.demo_enc_results = None
    if "demo_dec_results" not in st.session_state:
        st.session_state.demo_dec_results = None

    st.subheader("Pengaturan Kunci")
    col1, col2 = st.columns(2)
    with col1:
        caesar_shift = st.number_input(
            "Caesar Shift (1-25)", 
            min_value=1, 
            max_value=25, 
            value=7,
            key="demo_caesar_shift"
        )
    with col2:
        xor_key = st.text_input(
            "Kunci XOR (Teks)", 
            value="69",
            key="demo_xor_key"
        )
    st.markdown("---")

    tab1, tab2 = st.tabs(["Proses Enkripsi", "Proses Dekripsi"])

    with tab1:
        st.header("Enkripsi (Plaintext -> Ciphertext)")
        plaintext = st.text_area("1. Masukkan Teks (Plaintext):", key="demo_enc_input")

        if st.button("Enkripsi", key="btn_enc", use_container_width=True):
            if plaintext:
                try:
                    with st.spinner("Menjalankan proses enkripsi... (RSA mungkin butuh waktu)"):
                        caesar_encrypted = caesar.caesar_encrypt(plaintext, caesar_shift)
                        xor_encrypted = xor.xor_encrypt(caesar_encrypted, xor_key)
                        rsa_encrypted_list = rsa.rsa_encrypt(xor_encrypted)
                        final_ciphertext = ' '.join(map(str, rsa_encrypted_list))
                    
                    st.session_state.demo_enc_results = {
                        "step1": caesar_encrypted,
                        "step2": xor_encrypted,
                        "step3": rsa_encrypted_list,
                        "final": final_ciphertext
                    }
                    st.session_state.demo_dec_results = None 
                except Exception as e:
                    st.error(f"Terjadi error saat enkripsi: {e}")
                    st.session_state.demo_enc_results = None
            else:
                st.warning("Masukkan teks terlebih dahulu.")
        
        if st.session_state.demo_enc_results:
            results = st.session_state.demo_enc_results
            st.subheader(f"Langkah 1: Caesar Cipher (Shift {caesar_shift})")
            st.code(results["step1"], language="text")
            st.subheader(f"Langkah 2: XOR Cipher (Key \"{xor_key}\")")
            st.code(results["step2"], language="text")
            st.subheader("Langkah 3: RSA Encryption")
            st.json(results["step3"])
            st.subheader("Hasil Akhir (Siap kirim ke chat)")
            st.code(results["final"], language="text")

    with tab2:
        st.header("Dekripsi (Ciphertext -> Plaintext)")
        st.info("Copy ciphertext dari chat bubble dan paste di sini.")
        ciphertext = st.text_area("1. Masukkan Ciphertext (angka dipisah spasi):", key="demo_dec_input")

        if st.button("Dekripsi", key="btn_dec", use_container_width=True):
            if ciphertext:
                try:
                    with st.spinner("Menjalankan proses dekripsi... (RSA mungkin butuh waktu)"):
                        rsa_decrypted = rsa.rsa_decrypt(ciphertext)
                        xor_decrypted = xor.xor_decrypt(rsa_decrypted, xor_key)
                        caesar_decrypted = caesar.caesar_decrypt(xor_decrypted, caesar_shift)
                    
                    st.session_state.demo_dec_results = {
                        "step1": rsa_decrypted,
                        "step2": xor_decrypted,
                        "step3": caesar_decrypted
                    }
                    st.session_state.demo_enc_results = None
                except Exception as e:
                    st.error(f"Input tidak valid. Pastikan formatnya benar (angka dipisah spasi) dan kunci Anda benar. Error: {e}")
                    st.session_state.demo_dec_results = None
            else:
                st.warning("Masukkan ciphertext terlebih dahulu.")
        
        if st.session_state.demo_dec_results:
            results = st.session_state.demo_dec_results
            st.subheader("Langkah 1: RSA Decryption")
            st.code(results["step1"], language="text")
            st.subheader(f"Langkah 2: XOR Decrypt (Key \"{xor_key}\")")
            st.code(results["step2"], language="text")
            st.subheader(f"Langkah 3: Caesar Decrypt (Shift {caesar_shift})")
            st.code(results["step3"], language="text")
            st.subheader("Hasil Akhir (Plaintext)")
            st.success(results["step3"])
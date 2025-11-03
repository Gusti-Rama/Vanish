import streamlit as st
import pandas as pd
from app_core import init_connection, aes_cipher

st.set_page_config(page_title="Data Mahasiswa", layout="wide")
st.title("Data Akademik Mahasiswa")

if not st.session_state.get('logged_in'):
    st.warning("Anda harus login untuk melihat data mahasiswa.")
else:
    if st.session_state.get('user_role') not in ['admin', 'dosen']:
        st.error("Anda tidak memiliki izin untuk melihat data mahasiswa.")
    else:
        conn = init_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_data ORDER BY id DESC")
        students = cursor.fetchall()

        decrypted_data = []
        for student in students:
            try:
                nama = aes_cipher.decrypt(student['nama'])
            except Exception:
                nama = "<decryption error>"
            try:
                nilai = aes_cipher.decrypt(student['nilai'])
            except Exception:
                nilai = "<decryption error>"
            decrypted_data.append({
                'nim': student['nim'],
                'nama': nama,
                'nilai': nilai,
                'created_at': student['created_at']
            })

        df = pd.DataFrame(decrypted_data)
        st.dataframe(df)

        if st.session_state.get('user_role') == 'admin':
            st.markdown("---")
            st.subheader("Tambah Mahasiswa Baru")
            with st.form("add_student"):
                nim = st.text_input("NIM")
                nama = st.text_input("Nama")
                nilai = st.text_input("Nilai")
                submitted = st.form_submit_button("Tambah Mahasiswa")
                if submitted:
                    try:
                        cursor.execute(
                            "INSERT INTO student_data (nim, nama, nilai) VALUES (%s, %s, %s)",
                            (nim, aes_cipher.encrypt(nama), aes_cipher.encrypt(nilai))
                        )
                        conn.commit()
                        st.success("Data Mahasiswa berhasil ditambahkan")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

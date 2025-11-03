import streamlit as st
import tempfile
import os
import pandas as pd
from app_core import init_connection
from fungsi.steganography import encode_image, decode_image

st.set_page_config(page_title="Certificates", layout="centered")
st.title("Digital Certificates")

if not st.session_state.get('logged_in'):
    st.warning("You must be logged in to process certificates. Go to the Login page.")
else:
    uploaded_image = st.file_uploader("Upload Certificate (JPG/PNG)", type=['jpg', 'png'])
    if uploaded_image:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(uploaded_image.getvalue())
            temp_path = tmp_file.name

        secret_data = f"Authenticated by University on {pd.Timestamp.now()}"
        output_path = temp_path.replace('.png', '_marked.png')

        try:
            ok = encode_image(temp_path, secret_data, output_path)
        except Exception as e:
            ok = False
            st.error(f"Error processing image: {e}")

        if ok:
            st.success("Certificate processed successfully!")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Certificate")
                st.image(temp_path)
            with col2:
                st.subheader("Processed Certificate")
                st.image(output_path)
                if st.button("Verify Authenticity"):
                    try:
                        hidden_data = decode_image(output_path)
                        st.info(f"Certificate Authenticity: {hidden_data}")
                    except Exception:
                        st.error("Could not verify certificate authenticity")

        # cleanup
        try:
            os.unlink(temp_path)
            os.unlink(output_path)
        except Exception:
            pass

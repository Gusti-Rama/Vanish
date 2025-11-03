import streamlit as st
from app_core import init_connection
from fungsi.caesar import caesar_encrypt, caesar_decrypt
from fungsi.xor import xor_encrypt, xor_decrypt

st.set_page_config(page_title="Messages", layout="centered")
st.title("ini test")
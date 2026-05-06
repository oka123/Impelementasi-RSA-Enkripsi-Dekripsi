import streamlit as st
# ==========================================
# 1. KONFIGURASI & STATE MANAGEMENT
# ==========================================
# Konfigurasi halaman
def setup_page():
    st.set_page_config(
        page_title="RSA Crypto Dashboard",
        page_icon="🔐",
        layout="wide"
    )

# Konstanta
MAX_CHUNK_SIZE = 214
PASSWORD_KEY = b"kunciPrivate" # Password untuk private key

# Inisialisasi Session State untuk menyimpan kunci sementara di memori browser
def init_session():
    if 'private_key' not in st.session_state:
        st.session_state.private_key = None
    if 'public_key' not in st.session_state:
        st.session_state.public_key = None

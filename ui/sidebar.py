import streamlit as st
from cryptography.hazmat.primitives import serialization
from crypto_utils import generate_keys, get_pem_keys
from config import PASSWORD_KEY

def sidebar_menu():
    with st.sidebar:
        st.header("RSA System 🔐")
        st.info(f"User: **Misha**") # Personalisasi kecil
        menu = st.radio("Navigasi", ["Dashboard", "Enkripsi/Dekripsi Manual", "Proses File"])
        
        st.divider()
        st.subheader("🔑 Status Kunci")
        
        # Cek apakah kunci sudah ada di session state
        if st.session_state.private_key:
            st.success("Kunci Aktif ✅")
            
            # Tombol Download Kunci
            pem_priv, pem_pub = get_pem_keys(st.session_state.private_key, st.session_state.public_key)
            
            st.download_button("⬇️ Download Private Key", pem_priv, "private_key.pem", "application/x-pem-file")
            st.download_button("⬇️ Download Public Key", pem_pub, "public_key.pem", "application/x-pem-file")
            
            if st.button("Hapus Kunci (Logout)"):
                st.session_state.private_key = None
                st.session_state.public_key = None
                st.rerun()
        else:
            st.warning("Kunci Belum Dimuat ❌")
            if st.button("Buat Kunci Baru"):
                priv, pub = generate_keys()
                st.session_state.private_key = priv
                st.session_state.public_key = pub
                st.rerun()
                
            st.markdown("---")
            st.caption("Atau upload kunci yang ada:")
            uploaded_priv = st.file_uploader("Upload Private Key (.pem)", type=['pem'])
            if uploaded_priv:
                try:
                    priv_key_loaded = serialization.load_pem_private_key(
                        uploaded_priv.read(), password=PASSWORD_KEY
                    )
                    st.session_state.private_key = priv_key_loaded
                    st.session_state.public_key = priv_key_loaded.public_key()
                    st.success("Kunci berhasil dimuat!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal memuat kunci: {e}")

    return menu

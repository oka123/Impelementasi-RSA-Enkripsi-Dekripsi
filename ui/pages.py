import streamlit as st
import pandas as pd # type: ignore
import io
from typing import Any, cast
from cryptography.hazmat.primitives.asymmetric import rsa
from crypto_utils import chunked_encrypt_text, chunked_decrypt_text, get_pem_keys

def page_dashboard():
    st.title("📊 Dashboard Kriptografi RSA")
    st.markdown("Selamat datang di aplikasi keamanan data berbasis RSA-OAEP.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Algoritma", value="RSA-2048")
    with col2:
        st.metric(label="Hashing", value="SHA-256")
    with col3:
        status = "Aktif" if st.session_state.public_key else "Non-Aktif"
        st.metric(label="Status Sistem", value=status)

    st.markdown("---")
    st.subheader("Cara Kerja Sistem")
    st.info("""
    1. **Chunking**: Data dipecah menjadi bagian-bagian kecil (max 214 bytes).
    2. **Base64**: Data di-encode agar mendukung karakter non-teks.
    3. **Enkripsi**: Menggunakan Public Key.
    4. **Dekripsi**: Menggunakan Private Key.
    """)

def page_manual():
    st.title("✍️ Enkripsi & Dekripsi Manual")
    
    if not st.session_state.public_key:
        st.error("⚠️ Harap buat atau muat kunci terlebih dahulu di Sidebar!")
        return

    #-- Mengubah objek kunci menjadi teks yang bisa dibaca ---
    pem_priv, pem_pub = get_pem_keys(st.session_state.private_key, st.session_state.public_key)
    pub_text = pem_pub.decode('utf-8')
    priv_text = pem_priv.decode('utf-8')
    # -----------------------------------------------------------------------


    tab1, tab2 = st.tabs(["🔒 Enkripsi", "🔓 Dekripsi"])
    
    with tab1:
        # Menampilkan kunci publik dengan expander
        with st.expander("🔑 Lihat Detail Kunci Publik"):
            st.code(pub_text, language="text")
        
        text_input = st.text_area("Masukkan pesan teks:", height=150)
        if st.button("Enkripsi Pesan"):
            if text_input:
                # Menggunakan chunking logic agar konsisten
                cipher = chunked_encrypt_text(text_input, st.session_state.public_key)
                
                st.success("Enkripsi Berhasil!")
                st.code(cipher, language="text")
            else:
                st.warning("Masukkan teks dulu ya.")

    with tab2:
        # Menampilkan kunci private dengan expander
        with st.expander("🔑 Lihat Detail Kunci Private"):
            st.code(priv_text, language="text")
        
        cipher_input = st.text_area("Masukkan Ciphertext (Hex):", height=150)
        if st.button("Dekripsi Pesan"):
            if cipher_input:
                try:
                    plain = chunked_decrypt_text(cipher_input, st.session_state.private_key)
                    st.success("Dekripsi Berhasil!")
                    st.text_area("Hasil Plaintext:", value=plain, height=150)
                except Exception:
                    st.error("Gagal mendekripsi. Pastikan kunci cocok dan format benar.")

def page_file():
    st.title("📂 Proses File (CSV/Excel)")
    
    if not st.session_state.public_key:
        st.error("⚠️ Harap buat atau muat kunci terlebih dahulu di Sidebar!")
        return

    uploaded_file = st.file_uploader("Upload file CSV atau Excel", type=['csv', 'xlsx'])
    
    if uploaded_file:
        # Membaca file
        try:
            df: Any
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file) # type: ignore
            else:
                df = pd.read_excel(uploaded_file) # type: ignore
            
            st.write("Preview Data:", df.head())
            
            operation = st.radio("Pilih Operasi", ["Enkripsi Kolom", "Dekripsi Kolom"])
            column = st.selectbox("Pilih Kolom Target", df.columns)
            
            if st.button("Proses File"):
                with st.spinner("Sedang memproses..."):
                    df_result = df.copy()
                    
                    if operation == "Enkripsi Kolom":
                        pub_key = cast(rsa.RSAPublicKey, st.session_state.public_key)
                        df_result[column] = df_result[column].apply(
                            lambda x: chunked_encrypt_text(str(cast(Any, x)), pub_key) # type: ignore
                        )
                        output_filename = f"encrypted_{uploaded_file.name}"
                    else:
                        priv_key = cast(rsa.RSAPrivateKey, st.session_state.private_key)
                        df_result[column] = df_result[column].apply(
                            lambda x: chunked_decrypt_text(str(cast(Any, x)), priv_key) # type: ignore
                        )
                        output_filename = f"decrypted_{uploaded_file.name}"
                    
                    st.success("Selesai!")
                    st.write("Hasil:", df_result.head())
                    
                    # Konversi untuk download
                    if output_filename.endswith('.csv'):
                        data_csv = df_result.to_csv(index=False).encode('utf-8') # type: ignore
                        st.download_button("💾 Download Hasil CSV", data_csv, output_filename, "text/csv")
                    else:
                        buffer = io.BytesIO()
                        # Use cast(Any, ...) to bypass strict path-type errors in some pandas versions
                        with pd.ExcelWriter(cast(Any, buffer), engine='openpyxl') as writer: # type: ignore
                            df_result.to_excel(writer, index=False) # type: ignore
                        st.download_button("💾 Download Hasil Excel", buffer.getvalue(), output_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        
        except Exception as e:
            st.error(f"Error membaca file: {e}")

import streamlit as st
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from base64 import b64encode, b64decode
import pandas as pd
import os
import io

# ==========================================
# 1. KONFIGURASI & STATE MANAGEMENT
# ==========================================
st.set_page_config(
    page_title="RSA Crypto Dashboard",
    page_icon="🔐",
    layout="wide"
)

# Konstanta
MAX_CHUNK_SIZE = 214
PASSWORD_KEY = b"kunciPrivate" # Password untuk private key

# Inisialisasi Session State untuk menyimpan kunci sementara di memori browser
if 'private_key' not in st.session_state:
    st.session_state.private_key = None
if 'public_key' not in st.session_state:
    st.session_state.public_key = None

# ==========================================
# 2. FUNGSI LOGIKA (BACKEND)
# ==========================================

def generate_keys():
    """Membuat pasangan kunci baru"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def get_pem_keys(private_key, public_key):
    """Mengubah objek kunci menjadi format PEM (bytes) untuk di-download"""
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(PASSWORD_KEY)
    )
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_private, pem_public

def encrypt_bytes(data_bytes, public_key):
    """Enkripsi raw bytes"""
    return public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_bytes(ciphertext, private_key):
    """Dekripsi raw bytes"""
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def chunked_encrypt_text(text, public_key):
    """Fungsi helper untuk memecah teks, encode base64, dan enkripsi per chunk"""
    try:
        # 1. Konversi ke string & encode utf-8
        data_bytes = str(text).encode('utf-8')
        # 2. Encode Base64 agar aman untuk karakter aneh
        data_b64_bytes = b64encode(data_bytes)
        
        encrypted_chunks = []
        # 3. Looping per MAX_CHUNK_SIZE
        for i in range(0, len(data_b64_bytes), MAX_CHUNK_SIZE):
            chunk = data_b64_bytes[i:i + MAX_CHUNK_SIZE]
            encrypted_chunk = encrypt_bytes(chunk, public_key)
            encrypted_chunks.append(encrypted_chunk.hex())
            
        return ":".join(encrypted_chunks)
    except Exception as e:
        return f"[ERROR] {e}"

def chunked_decrypt_text(encrypted_string, private_key):
    """Fungsi helper untuk dekripsi chunk hex kembali ke teks asli"""
    try:
        if not isinstance(encrypted_string, str): return str(encrypted_string)
        
        encrypted_chunks_hex = encrypted_string.split(":")
        decrypted_b64_bytes = b''
        
        for hex_chunk in encrypted_chunks_hex:
            ciphertext_bytes = bytes.fromhex(hex_chunk)
            decrypted_b64_bytes += decrypt_bytes(ciphertext_bytes, private_key)
            
        # Decode Base64 kembali ke bytes asli, lalu ke string
        original_bytes = b64decode(decrypted_b64_bytes)
        return original_bytes.decode('utf-8')
    except Exception as e:
        return f"[ERROR] {e}"

# ==========================================
# 3. TAMPILAN UI (FRONTEND)
# ==========================================

def sidebar_menu():
    with st.sidebar:
        st.header("RSA System 🔐")
        st.info(f"User: **Kelompok 1A**") # Personalisasi kecil
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
        text_input = st.text_area("Masukkan pesan teks:", height=150)
        if st.button("Enkripsi Pesan"):
            if text_input:
                # Menggunakan chunking logic agar konsisten
                cipher = chunked_encrypt_text(text_input, st.session_state.public_key)

                # Menampilkan kunci publik yang sudah jadi teks
                st.write("**input kunci Public =**")
                st.code(pub_text, language="text")
                
                
                st.success("Enkripsi Berhasil!")
                st.code(cipher, language="text")
            else:
                st.warning("Masukkan teks dulu ya.")

    with tab2:
        cipher_input = st.text_area("Masukkan Ciphertext (Hex):", height=150)
        if st.button("Dekripsi Pesan"):
            if cipher_input:
                try:
                    plain = chunked_decrypt_text(cipher_input, st.session_state.private_key)
                    
                    # Menampilkan kunci private yang sudah jadi teks
                    st.write("**input kunci Private =**")
                    st.code(priv_text, language="text")

                    st.success("Dekripsi Berhasil!")
                    st.text_area("Hasil Plaintext:", value=plain, height=150)
                except Exception as e:
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
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("Preview Data:", df.head())
            
            operation = st.radio("Pilih Operasi", ["Enkripsi Kolom", "Dekripsi Kolom"])
            column = st.selectbox("Pilih Kolom Target", df.columns)
            
            if st.button("Proses File"):
                with st.spinner("Sedang memproses..."):
                    df_result = df.copy()
                    
                    if operation == "Enkripsi Kolom":
                        df_result[column] = df_result[column].apply(
                            lambda x: chunked_encrypt_text(x, st.session_state.public_key)
                        )
                        output_filename = f"encrypted_{uploaded_file.name}"
                    else:
                        df_result[column] = df_result[column].apply(
                            lambda x: chunked_decrypt_text(x, st.session_state.private_key)
                        )
                        output_filename = f"decrypted_{uploaded_file.name}"
                    
                    st.success("Selesai!")
                    st.write("Hasil:", df_result.head())
                    
                    # Konversi untuk download
                    if output_filename.endswith('.csv'):
                        data_csv = df_result.to_csv(index=False).encode('utf-8')
                        st.download_button("💾 Download Hasil CSV", data_csv, output_filename, "text/csv")
                    else:
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df_result.to_excel(writer, index=False)
                        st.download_button("💾 Download Hasil Excel", buffer.getvalue(), output_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        
        except Exception as e:
            st.error(f"Error membaca file: {e}")

# ==========================================
# 4. MAIN APP
# ==========================================
def main():
    menu = sidebar_menu()
    
    if menu == "Dashboard":
        page_dashboard()
    elif menu == "Enkripsi/Dekripsi Manual":
        page_manual()
    elif menu == "Proses File":
        page_file()

if __name__ == "__main__":
    main()
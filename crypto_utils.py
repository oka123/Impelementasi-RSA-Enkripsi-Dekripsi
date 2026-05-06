from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from base64 import b64encode, b64decode
from typing import Tuple, List
from config import MAX_CHUNK_SIZE, PASSWORD_KEY

# ==========================================
# 2. FUNGSI LOGIKA (BACKEND)
# ==========================================

def generate_keys() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Membuat pasangan kunci baru"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def get_pem_keys(private_key: rsa.RSAPrivateKey, public_key: rsa.RSAPublicKey) -> Tuple[bytes, bytes]:
    """ Mengubah objek kunci menjadi format PEM (bytes) untuk di-download """   

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

def encrypt_bytes(data_bytes: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    """Enkripsi raw bytes"""
    return public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_bytes(ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """Dekripsi raw bytes"""
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def chunked_encrypt_text(text: str, public_key: rsa.RSAPublicKey) -> str:
    """Fungsi helper untuk memecah teks, encode base64, dan enkripsi per chunk"""
    try:
        # 1. Konversi ke string & encode utf-8
        data_bytes = str(text).encode('utf-8')
        # 2. Encode Base64 agar aman untuk karakter aneh
        data_b64_bytes = b64encode(data_bytes)
        
        encrypted_chunks: List[str] = []
        # 3. Looping per MAX_CHUNK_SIZE
        for i in range(0, len(data_b64_bytes), MAX_CHUNK_SIZE):
            chunk = data_b64_bytes[i:i + MAX_CHUNK_SIZE]
            encrypted_chunk = encrypt_bytes(chunk, public_key)
            encrypted_chunks.append(encrypted_chunk.hex())
            
        return ":".join(encrypted_chunks)
    except Exception as e:
        return f"[ERROR] {e}"

def chunked_decrypt_text(encrypted_string: str, private_key: rsa.RSAPrivateKey) -> str:
    """Fungsi helper untuk dekripsi chunk hex kembali ke teks asli"""
    try:
        encrypted_chunks_hex = encrypted_string.split(":")
        decrypted_b64_bytes: bytes = b''
        
        for hex_chunk in encrypted_chunks_hex:
            ciphertext_bytes = bytes.fromhex(hex_chunk)
            decrypted_b64_bytes += decrypt_bytes(ciphertext_bytes, private_key)
            
        # Decode Base64 kembali ke bytes asli, lalu ke string
        original_bytes = b64decode(decrypted_b64_bytes)
        return original_bytes.decode('utf-8')
    except Exception as e:
        return f"[ERROR] {e}"

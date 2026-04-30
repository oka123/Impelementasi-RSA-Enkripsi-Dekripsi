<<<<<<< HEAD
# install library jika belum ada, bisa di uncomment.
# %pip install cryptography pandas --quiet

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from base64 import b64encode, b64decode # Digunakan untuk enkoding data non-teks
import pandas as pd
import os
import io

#Konfigurasi dan Batasan
private_key = None
public_key = None
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

# Batasan RSA-2048 OAEP SHA256: Hanya dapat mengenkripsi maks 214 bytes per blok.
MAX_CHUNK_SIZE = 214 
# Batasan ukuran file yang diminta: 1 MB
MAX_FILE_SIZE_BYTES = 1024 * 1024 # 1 Megabyte

#Simpan kunci
def save_keys(private_key, public_key):
    """Menyimpan kunci ke file PEM, kunci privat dienkripsi dengan password."""
    # NOTE: Ganti 'password' dengan password yang kuat.
    PASSWORD = b"kemdatRSA" 
    try:
        # Menyimpan Kunci Privat (terenkripsi)
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(PASSWORD) 
        )
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(pem_private)

        # Menyimpan Kunci Publik
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(pem_public)
            
        print(f"✅ Kunci privat dan publik berhasil disimpan ke '{PRIVATE_KEY_FILE}' dan '{PUBLIC_KEY_FILE}'")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan kunci: {e}")


def load_keys():
    """Memuat kunci dari file PEM."""
    PASSWORD = b"kemdatRSA" 
    try:
        # Memuat Kunci Privat
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=PASSWORD)
        
        # Memuat Kunci Publik
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
            
        return private_key, public_key

    except FileNotFoundError:
        return None, None
    except ValueError as e:
        print(f"[ERROR] Gagal memuat kunci. Password atau format file salah: {e}")
        return None, None

#Proses RSA
def encrypt_data(data_bytes: bytes) -> bytes:
    """Enkripsi satu chunk data (maks 214 bytes)."""
    if public_key is None: raise Exception("Kunci publik belum dimuat.")
    if len(data_bytes) > MAX_CHUNK_SIZE: 
        raise ValueError("Data chunk terlalu besar.")
        
    return public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_data(ciphertext: bytes) -> bytes:
    """Dekripsi satu blok ciphertext."""
    if private_key is None: raise Exception("Kunci privat belum dimuat.")
        
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

#Manual
def enkripsi_manual():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    plaintext = input(f"Masukkan teks yang ingin dienkripsi (Maksimal {MAX_CHUNK_SIZE} karakter): ")
    
    data_bytes = plaintext.encode('utf-8')
    if len(data_bytes) > MAX_CHUNK_SIZE:
         print(f"[ERROR] Pesan terlalu panjang. RSA hanya dapat mengenkripsi {MAX_CHUNK_SIZE} bytes.")
         return
         
    try:
        ciphertext_bytes = encrypt_data(data_bytes)
        # OUTPUT: hasil enkripsi ditampilkan dalam bentuk ciphertext (heksadesimal)
        print("\nHasil pesan yang sudah dienkripsi (heksadesimal):\n", ciphertext_bytes.hex())
    except Exception as e:
        print(f"[ERROR] Gagal enkripsi manual: {e}")


def dekripsi_manual():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    ciphertext_hex = input("Masukkan ciphertext (heksadesimal) yang ingin didekripsi: ")
    
    try:
        ciphertext_bytes = bytes.fromhex(ciphertext_hex)
        plaintext_bytes = decrypt_data(ciphertext_bytes)
        # OUTPUT: hasil dekripsi berupa teks asli
        print("\nHasil pesan yang sudah didekripsi (teks asli):\n", plaintext_bytes.decode('utf-8'))
    except ValueError:
        print("[ERROR] Input heksadesimal tidak valid.")
    except Exception as e:
        print(f"[ERROR] Gagal dekripsi manual: {e}")


#File
# === Fungsi enkripsi file ===
def enkripsi_file():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    filetype = input("Masukkan jenis file (csv/xlsx): ").strip().lower()

    if filetype == "exit": return "exit"
    if filetype not in ["csv", "xlsx"]:
        print("[ERROR] Jenis file tidak valid! Pilih antara 'csv' atau 'xlsx'."); return None

    filename = input(f"Masukkan nama file {filetype.upper()} (e.g., data.{filetype}): ").strip()
    
    if not os.path.exists(filename):
        print(f"[ERROR] File '{filename}' tidak ditemukan."); return None

    # PENGECEKAN UKURAN FILE (MAX 1 MB)
    file_size = os.path.getsize(filename)
    if file_size > MAX_FILE_SIZE_BYTES:
        print(f"[ERROR] Ukuran file ({file_size / MAX_FILE_SIZE_BYTES:.2f} MB) melebihi batas maksimum 1 MB. Proses dibatalkan."); return None
    # ----------------------------

    print(f"\n✅ File '{filename}' berhasil ditemukan ({file_size / 1024:.2f} KB) dan akan diproses!\n")

    # Baca file
    try:
        if filetype == "csv": df = pd.read_csv(filename)
        else: df = pd.read_excel(filename)
    except Exception as e:
         print(f"[ERROR] Gagal membaca file: {e}"); return None

    print("\nKolom tersedia:", list(df.columns))
    column = input("Masukkan nama kolom yang akan dienkripsi: ").strip()
    
    if column.lower() == "exit":
        print("\n˙⋆✮ Proses dibatalkan. Kembali ke menu utama. ✮⋆˙"); return None
    if column not in df.columns:
        print("[ERROR] Kolom tidak ditemukan!"); return None

    # Proses enkripsi dengan CHUNKING dan BASE64
    df_result = pd.DataFrame()
    df_result["index"] = df.index
    
    def chunked_encrypt(value):
        # Konversi nilai apapun menjadi string, lalu encoding menjadi bytes (sebagai langkah awal)
        data_bytes = str(value).encode('utf-8')
        
        # Enkoding Base64 untuk menangani byte non-teks secara universal
        # dan memastikan data string hasil Base64 ini yang di-chunk
        data_b64_bytes = b64encode(data_bytes)
        
        encrypted_chunks = []
        
        # Pisahkan data per MAX_CHUNK_SIZE (214 bytes)
        for i in range(0, len(data_b64_bytes), MAX_CHUNK_SIZE):
            chunk = data_b64_bytes[i:i + MAX_CHUNK_SIZE]
            try:
                encrypted_chunk = encrypt_data(chunk)
                # Simpan chunk terenkripsi dalam format hex
                encrypted_chunks.append(encrypted_chunk.hex()) 
            except Exception as e:
                return f"[ENCRYPTION_ERROR] {e}"
        
        # Gabungkan semua chunk yang sudah dienkripsi dengan delimiter ":"
        return ":".join(encrypted_chunks)

    df_result["encrypted_text"] = df[column].apply(chunked_encrypt)

    # Simpan hasil (sesuai format: encrypted_namaFile.formatFile)
    base_name, _ = os.path.splitext(filename)
    output_name = f"encrypted_{os.path.basename(base_name)}.{filetype}"
    if filetype == "csv": df_result.to_csv(output_name, index=False)
    else: df_result.to_excel(output_name, index=False)

    print(f"\n✅ File terenkripsi berhasil disimpan sebagai '{output_name}'!")
    print(f"💾 File tersimpan di direktori: {os.getcwd()}\n") # Mencapai persyaratan 'File hasil dapat diunduh'
    return None


# === Fungsi dekripsi file ===
def dekripsi_file():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    filetype = input("Masukkan jenis file terenkripsi (csv/xlsx): ").strip().lower()

    if filetype == "exit": return "exit"
    if filetype not in ["csv", "xlsx"]:
        print("[ERROR] Jenis file tidak valid! Pilih antara 'csv' atau 'xlsx'."); return None

    filename = input(f"Masukkan nama file terenkripsi {filetype.upper()} (e.g., encrypted_data.{filetype}): ").strip()
    
    if not os.path.exists(filename):
        print(f"[ERROR] File '{filename}' tidak ditemukan."); return None

    # PENGECEKAN UKURAN FILE (MAX 1 MB)
    file_size = os.path.getsize(filename)
    if file_size > MAX_FILE_SIZE_BYTES:
        print(f"[ERROR] Ukuran file ({file_size / MAX_FILE_SIZE_BYTES:.2f} MB) melebihi batas maksimum 1 MB. Proses dibatalkan."); return None
    # ----------------------------

    print(f"\n✅ File '{filename}' berhasil ditemukan ({file_size / 1024:.2f} KB) dan akan diproses!\n")

    # Baca file
    try:
        if filetype == "csv": df = pd.read_csv(filename)
        else: df = pd.read_excel(filename)
    except Exception as e:
         print(f"[ERROR] Gagal membaca file: {e}"); return None
         
    if "encrypted_text" not in df.columns:
         print("[ERROR] Kolom 'encrypted_text' tidak ditemukan dalam file!"); return None

    # Proses dekripsi dengan DE-CHUNKING dan BASE64
    df_result = pd.DataFrame()
    df_result["index"] = df["index"]
    
    def chunked_decrypt(encrypted_data_string):
        if not isinstance(encrypted_data_string, str) or "[ENCRYPTION_ERROR]" in encrypted_data_string:
            return str(encrypted_data_string) 
            
        encrypted_chunks_hex = encrypted_data_string.split(":")
        decrypted_b64_bytes = b''
        
        for hex_chunk in encrypted_chunks_hex:
            try:
                ciphertext_bytes = bytes.fromhex(hex_chunk)
                decrypted_b64_bytes += decrypt_data(ciphertext_bytes)
            except Exception as e:
                return f"[DECRYPTION_ERROR] Gagal dekripsi chunk: {e}"
        
        # Kembalikan ke nilai asli (string/bytes) dari Base64
        try:
            # Lakukan Base64 decode
            original_bytes = b64decode(decrypted_b64_bytes)
            # Karena awalnya diasumsikan string, coba decode ke string
            return original_bytes.decode('utf-8')
        except Exception as e:
            # Jika gagal di-decode ke string (misalnya itu data biner), kembalikan representasi hex
            return f"[BINARY_DATA_HEX] {original_bytes.hex()}"


    df_result["decrypted_text"] = df["encrypted_text"].apply(chunked_decrypt)

    # Simpan hasil (sesuai format: decrypted_namaFile.formatFile)
    base_name, _ = os.path.splitext(filename)
    clean_name = os.path.basename(base_name).replace("encrypted_", "") 
    output_name = f"decrypted_{clean_name}.{filetype}"

    if filetype == "csv": df_result.to_csv(output_name, index=False)
    else: df_result.to_excel(output_name, index=False)

    print(f"\n✅ File hasil dekripsi berhasil disimpan sebagai '{output_name}'!")
    print(f"💾 File tersimpan di direktori: {os.getcwd()}\n")
    return None

# Aplikasi
def main():
    print("˙⋆✮ Selamat datang di aplikasi kriptografi sederhana RSA-OAEP! ✮⋆˙")
    
    # PROSES: Memuat atau Membuat Kunci Persisten
    global private_key, public_key
    private_key, public_key = load_keys()
    
    if private_key is None:
        print("[INFO] Membuat pasangan kunci RSA-2048 baru...")
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        save_keys(private_key, public_key)
        
    print("✅ Kunci berhasil dimuat dan siap digunakan!")
    
    mode()

def mode():
    while True:
        # INPUT: Pilih Mode Input
        print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Ketik 'Exit' kapan saja untuk keluar dari program.\n")
        print("Pilih mode input [1/2]:\n")
        print("1. Manual")
        print("2. Dari file (csv/xlsx)\n")

        mode_input = input("Masukkan pilihan mode: ").strip().lower()

        if mode_input == "exit":
            print("\n˙⋆✮ Sampai jumpa lagi! ✮⋆˙")
            break

        elif mode_input in ["1", "2"]:
            result = operasi(mode_input)
            if result == "exit":
                break
        else:
            print("Pilihan mode tidak valid! Coba lagi ya [1/2].")


def operasi(mode_input):
    while True:
        # INPUT: Tentukan Mode Operasi
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Pilih mode operasi [1/2]:\n")
        print("1. Enkripsi pesan")
        print("2. Dekripsi pesan\n")

        print("Ketik back untuk kembali yaa")
        operasi_input = input("Masukkan pilihan operasi: ").strip().lower()

        if operasi_input == "exit":
            print("\n˙⋆✮ Sampai jumpa lagi! ✮⋆˙")
            return "exit"
        elif operasi_input== "back":
            print("\nKembali ke mode input...")
            return

        # PROSES & OUTPUT
        if mode_input == "1":  # mode manual
            if operasi_input == "1": enkripsi_manual(); break
            elif operasi_input == "2": dekripsi_manual(); break
            else: print("Pilihan operasi tidak valid! Coba lagi ya [1/2].")

        elif mode_input == "2":  # mode file
            if operasi_input == "1": result = enkripsi_file()
            elif operasi_input == "2": result = dekripsi_file()
            else: print("Pilihan operasi tidak valid! Coba lagi ya [1/2]."); continue

            if result == "exit": return "exit"

        else:
            print("Pilihan mode tidak valid!"); continue

if __name__ == "__main__":
    main()
=======
# install library jika belum ada, bisa di uncomment.
# %pip install cryptography pandas --quiet

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from base64 import b64encode, b64decode # Digunakan untuk enkoding data non-teks
import pandas as pd
import os
import io

#Konfigurasi dan Batasan
private_key = None
public_key = None
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

# Batasan RSA-2048 OAEP SHA256: Hanya dapat mengenkripsi maks 214 bytes per blok.
MAX_CHUNK_SIZE = 214 
# Batasan ukuran file yang diminta: 1 MB
MAX_FILE_SIZE_BYTES = 1024 * 1024 # 1 Megabyte

#Simpan kunci
def save_keys(private_key, public_key):
    """Menyimpan kunci ke file PEM, kunci privat dienkripsi dengan password."""
    # NOTE: Ganti 'password' dengan password yang kuat.
    PASSWORD = b"kemdatRSA" 
    try:
        # Menyimpan Kunci Privat (terenkripsi)
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(PASSWORD) 
        )
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(pem_private)

        # Menyimpan Kunci Publik
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(pem_public)
            
        print(f"✅ Kunci privat dan publik berhasil disimpan ke '{PRIVATE_KEY_FILE}' dan '{PUBLIC_KEY_FILE}'")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan kunci: {e}")


def load_keys():
    """Memuat kunci dari file PEM."""
    PASSWORD = b"kemdatRSA" 
    try:
        # Memuat Kunci Privat
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=PASSWORD)
        
        # Memuat Kunci Publik
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
            
        return private_key, public_key

    except FileNotFoundError:
        return None, None
    except ValueError as e:
        print(f"[ERROR] Gagal memuat kunci. Password atau format file salah: {e}")
        return None, None

#Proses RSA
def encrypt_data(data_bytes: bytes) -> bytes:
    """Enkripsi satu chunk data (maks 214 bytes)."""
    if public_key is None: raise Exception("Kunci publik belum dimuat.")
    if len(data_bytes) > MAX_CHUNK_SIZE: 
        raise ValueError("Data chunk terlalu besar.")
        
    return public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_data(ciphertext: bytes) -> bytes:
    """Dekripsi satu blok ciphertext."""
    if private_key is None: raise Exception("Kunci privat belum dimuat.")
        
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

#Manual
def enkripsi_manual():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    plaintext = input(f"Masukkan teks yang ingin dienkripsi (Maksimal {MAX_CHUNK_SIZE} karakter): ")
    
    data_bytes = plaintext.encode('utf-8')
    if len(data_bytes) > MAX_CHUNK_SIZE:
         print(f"[ERROR] Pesan terlalu panjang. RSA hanya dapat mengenkripsi {MAX_CHUNK_SIZE} bytes.")
         return
         
    try:
        ciphertext_bytes = encrypt_data(data_bytes)
        # OUTPUT: hasil enkripsi ditampilkan dalam bentuk ciphertext (heksadesimal)
        print("\nHasil pesan yang sudah dienkripsi (heksadesimal):\n", ciphertext_bytes.hex())
    except Exception as e:
        print(f"[ERROR] Gagal enkripsi manual: {e}")


def dekripsi_manual():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    ciphertext_hex = input("Masukkan ciphertext (heksadesimal) yang ingin didekripsi: ")
    
    try:
        ciphertext_bytes = bytes.fromhex(ciphertext_hex)
        plaintext_bytes = decrypt_data(ciphertext_bytes)
        # OUTPUT: hasil dekripsi berupa teks asli
        print("\nHasil pesan yang sudah didekripsi (teks asli):\n", plaintext_bytes.decode('utf-8'))
    except ValueError:
        print("[ERROR] Input heksadesimal tidak valid.")
    except Exception as e:
        print(f"[ERROR] Gagal dekripsi manual: {e}")


#File
# === Fungsi enkripsi file ===
def enkripsi_file():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    filetype = input("Masukkan jenis file (csv/xlsx): ").strip().lower()

    if filetype == "exit": return "exit"
    if filetype not in ["csv", "xlsx"]:
        print("[ERROR] Jenis file tidak valid! Pilih antara 'csv' atau 'xlsx'."); return None

    filename = input(f"Masukkan nama file {filetype.upper()} (e.g., data.{filetype}): ").strip()
    
    if not os.path.exists(filename):
        print(f"[ERROR] File '{filename}' tidak ditemukan."); return None

    # PENGECEKAN UKURAN FILE (MAX 1 MB)
    file_size = os.path.getsize(filename)
    if file_size > MAX_FILE_SIZE_BYTES:
        print(f"[ERROR] Ukuran file ({file_size / MAX_FILE_SIZE_BYTES:.2f} MB) melebihi batas maksimum 1 MB. Proses dibatalkan."); return None
    # ----------------------------

    print(f"\n✅ File '{filename}' berhasil ditemukan ({file_size / 1024:.2f} KB) dan akan diproses!\n")

    # Baca file
    try:
        if filetype == "csv": df = pd.read_csv(filename)
        else: df = pd.read_excel(filename)
    except Exception as e:
         print(f"[ERROR] Gagal membaca file: {e}"); return None

    print("\nKolom tersedia:", list(df.columns))
    column = input("Masukkan nama kolom yang akan dienkripsi: ").strip()
    
    if column.lower() == "exit":
        print("\n˙⋆✮ Proses dibatalkan. Kembali ke menu utama. ✮⋆˙"); return None
    if column not in df.columns:
        print("[ERROR] Kolom tidak ditemukan!"); return None

    # Proses enkripsi dengan CHUNKING dan BASE64
    df_result = pd.DataFrame()
    df_result["index"] = df.index
    
    def chunked_encrypt(value):
        # Konversi nilai apapun menjadi string, lalu encoding menjadi bytes (sebagai langkah awal)
        data_bytes = str(value).encode('utf-8')
        
        # Enkoding Base64 untuk menangani byte non-teks secara universal
        # dan memastikan data string hasil Base64 ini yang di-chunk
        data_b64_bytes = b64encode(data_bytes)
        
        encrypted_chunks = []
        
        # Pisahkan data per MAX_CHUNK_SIZE (214 bytes)
        for i in range(0, len(data_b64_bytes), MAX_CHUNK_SIZE):
            chunk = data_b64_bytes[i:i + MAX_CHUNK_SIZE]
            try:
                encrypted_chunk = encrypt_data(chunk)
                # Simpan chunk terenkripsi dalam format hex
                encrypted_chunks.append(encrypted_chunk.hex()) 
            except Exception as e:
                return f"[ENCRYPTION_ERROR] {e}"
        
        # Gabungkan semua chunk yang sudah dienkripsi dengan delimiter ":"
        return ":".join(encrypted_chunks)

    df_result["encrypted_text"] = df[column].apply(chunked_encrypt)

    # Simpan hasil (sesuai format: encrypted_namaFile.formatFile)
    base_name, _ = os.path.splitext(filename)
    output_name = f"encrypted_{os.path.basename(base_name)}.{filetype}"
    if filetype == "csv": df_result.to_csv(output_name, index=False)
    else: df_result.to_excel(output_name, index=False)

    print(f"\n✅ File terenkripsi berhasil disimpan sebagai '{output_name}'!")
    print(f"💾 File tersimpan di direktori: {os.getcwd()}\n") # Mencapai persyaratan 'File hasil dapat diunduh'
    return None


# === Fungsi dekripsi file ===
def dekripsi_file():
    print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
    filetype = input("Masukkan jenis file terenkripsi (csv/xlsx): ").strip().lower()

    if filetype == "exit": return "exit"
    if filetype not in ["csv", "xlsx"]:
        print("[ERROR] Jenis file tidak valid! Pilih antara 'csv' atau 'xlsx'."); return None

    filename = input(f"Masukkan nama file terenkripsi {filetype.upper()} (e.g., encrypted_data.{filetype}): ").strip()
    
    if not os.path.exists(filename):
        print(f"[ERROR] File '{filename}' tidak ditemukan."); return None

    # PENGECEKAN UKURAN FILE (MAX 1 MB)
    file_size = os.path.getsize(filename)
    if file_size > MAX_FILE_SIZE_BYTES:
        print(f"[ERROR] Ukuran file ({file_size / MAX_FILE_SIZE_BYTES:.2f} MB) melebihi batas maksimum 1 MB. Proses dibatalkan."); return None
    # ----------------------------

    print(f"\n✅ File '{filename}' berhasil ditemukan ({file_size / 1024:.2f} KB) dan akan diproses!\n")

    # Baca file
    try:
        if filetype == "csv": df = pd.read_csv(filename)
        else: df = pd.read_excel(filename)
    except Exception as e:
         print(f"[ERROR] Gagal membaca file: {e}"); return None
         
    if "encrypted_text" not in df.columns:
         print("[ERROR] Kolom 'encrypted_text' tidak ditemukan dalam file!"); return None

    # Proses dekripsi dengan DE-CHUNKING dan BASE64
    df_result = pd.DataFrame()
    df_result["index"] = df["index"]
    
    def chunked_decrypt(encrypted_data_string):
        if not isinstance(encrypted_data_string, str) or "[ENCRYPTION_ERROR]" in encrypted_data_string:
            return str(encrypted_data_string) 
            
        encrypted_chunks_hex = encrypted_data_string.split(":")
        decrypted_b64_bytes = b''
        
        for hex_chunk in encrypted_chunks_hex:
            try:
                ciphertext_bytes = bytes.fromhex(hex_chunk)
                decrypted_b64_bytes += decrypt_data(ciphertext_bytes)
            except Exception as e:
                return f"[DECRYPTION_ERROR] Gagal dekripsi chunk: {e}"
        
        # Kembalikan ke nilai asli (string/bytes) dari Base64
        try:
            # Lakukan Base64 decode
            original_bytes = b64decode(decrypted_b64_bytes)
            # Karena awalnya diasumsikan string, coba decode ke string
            return original_bytes.decode('utf-8')
        except Exception as e:
            # Jika gagal di-decode ke string (misalnya itu data biner), kembalikan representasi hex
            return f"[BINARY_DATA_HEX] {original_bytes.hex()}"


    df_result["decrypted_text"] = df["encrypted_text"].apply(chunked_decrypt)

    # Simpan hasil (sesuai format: decrypted_namaFile.formatFile)
    base_name, _ = os.path.splitext(filename)
    clean_name = os.path.basename(base_name).replace("encrypted_", "") 
    output_name = f"decrypted_{clean_name}.{filetype}"

    if filetype == "csv": df_result.to_csv(output_name, index=False)
    else: df_result.to_excel(output_name, index=False)

    print(f"\n✅ File hasil dekripsi berhasil disimpan sebagai '{output_name}'!")
    print(f"💾 File tersimpan di direktori: {os.getcwd()}\n")
    return None

# Aplikasi
def main():
    print("˙⋆✮ Selamat datang di aplikasi kriptografi sederhana RSA-OAEP! ✮⋆˙")
    
    # PROSES: Memuat atau Membuat Kunci Persisten
    global private_key, public_key
    private_key, public_key = load_keys()
    
    if private_key is None:
        print("[INFO] Membuat pasangan kunci RSA-2048 baru...")
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        save_keys(private_key, public_key)
        
    print("✅ Kunci berhasil dimuat dan siap digunakan!")
    
    mode()

def mode():
    while True:
        # INPUT: Pilih Mode Input
        print("━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Ketik 'Exit' kapan saja untuk keluar dari program.\n")
        print("Pilih mode input [1/2]:\n")
        print("1. Manual")
        print("2. Dari file (csv/xlsx)\n")

        mode_input = input("Masukkan pilihan mode: ").strip().lower()

        if mode_input == "exit":
            print("\n˙⋆✮ Sampai jumpa lagi! ✮⋆˙")
            break

        elif mode_input in ["1", "2"]:
            result = operasi(mode_input)
            if result == "exit":
                break
        else:
            print("Pilihan mode tidak valid! Coba lagi ya [1/2].")


def operasi(mode_input):
    while True:
        # INPUT: Tentukan Mode Operasi
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━⊱⋆⊰━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Pilih mode operasi [1/2]:\n")
        print("1. Enkripsi pesan")
        print("2. Dekripsi pesan\n")

        print("Ketik back untuk kembali yaa")
        operasi_input = input("Masukkan pilihan operasi: ").strip().lower()

        if operasi_input == "exit":
            print("\n˙⋆✮ Sampai jumpa lagi! ✮⋆˙")
            return "exit"
        elif operasi_input== "back":
            print("\nKembali ke mode input...")
            return

        # PROSES & OUTPUT
        if mode_input == "1":  # mode manual
            if operasi_input == "1": enkripsi_manual(); break
            elif operasi_input == "2": dekripsi_manual(); break
            else: print("Pilihan operasi tidak valid! Coba lagi ya [1/2].")

        elif mode_input == "2":  # mode file
            if operasi_input == "1": result = enkripsi_file()
            elif operasi_input == "2": result = dekripsi_file()
            else: print("Pilihan operasi tidak valid! Coba lagi ya [1/2]."); continue

            if result == "exit": return "exit"

        else:
            print("Pilihan mode tidak valid!"); continue

if __name__ == "__main__":
    main()
>>>>>>> 7af547c36cc7bcc5b0860a581f034f8b680f8a5a

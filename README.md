# RSA-2048 OAEP — Aplikasi Kriptografi Sederhana

Aplikasi ini merupakan implementasi algoritma **RSA-2048 dengan OAEP (Optimal Asymmetric Encryption Padding)** menggunakan **Python**.  
Tujuannya adalah memahami konsep **kriptografi asimetris** serta penerapannya dalam pengamanan data seperti metadata dan API keys.

---

## Deskripsi
Aplikasi memiliki dua mode utama:
- **Manual** → untuk enkripsi dan dekripsi teks langsung melalui terminal.  
- **File (CSV/XLSX)** → untuk mengenkripsi atau mendekripsi kolom tertentu dari file data.  

Tersedia dua versi implementasi:
- **Lokal (Python)** → berjalan di komputer dan menyimpan hasil pada direktori yang sama.  
- **Google Colab** → dapat dijalankan secara online melalui tautan berikut:  
  [Buka di Google Colab](https://colab.research.google.com/drive/1CRv0oapQweG3RqIU-owNNLQOcB1uPqUb?usp=sharing)

---

## Fitur
- Enkripsi dan dekripsi teks serta file  
- Output ciphertext dalam format heksadesimal  
- Penamaan hasil otomatis (`encrypted_` / `decrypted_`)  
- Validasi input dan pesan kesalahan yang ramah pengguna  
- Integrasi dengan **Pandas** untuk pemrosesan data dalam file CSV/XLSX  

---

## Cara Kerja Singkat
1. Pengguna memilih mode input (manual atau file).  
2. Memilih operasi enkripsi atau dekripsi.  
3. Jika mode file dipilih, sistem meminta jenis file dan kolom target.  
4. Proses RSA-OAEP dijalankan untuk mengenkripsi atau mendekripsi data.  
5. Hasil disimpan otomatis dengan format:
   - `encrypted_namaFile.csv`
   - `decrypted_namaFile.csv`

---

## Kesimpulan
Aplikasi berhasil mengimplementasikan **RSA-2048 OAEP** secara sederhana dan modular.  
Proyek ini memberikan pemahaman praktis tentang kriptografi asimetris serta penerapannya dalam menjaga keamanan data di bidang data science.

---

## Kontributor
**Risma Febriyanti**  
[rismafebriyanti@mail.com](mailto:rismafebriyanti@gmail.com)

## Public APP
Streamlit : [RSA Crypto](https://q2cmadfbb9vtkcxokdfaqq.streamlit.app/)

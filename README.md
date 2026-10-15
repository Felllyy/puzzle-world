# Puzzle World

Aplikasi web lokal untuk membuat puzzle dari gambar dan menyusunnya kembali. Dibuat dengan Python, Streamlit, Pillow, OpenCV, dan NumPy.

## Persyaratan

Python 3.10 atau lebih baru di Windows, macOS, atau Linux.

## Instalasi dan menjalankan

Buka terminal di folder `puzzle_world`, lalu buat lingkungan virtual:

**Windows (PowerShell)**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit akan menampilkan alamat lokal, biasanya `http://localhost:8501`.

## Alur Generator → Solver

1. Pada **Puzzle Generator**, unggah JPG/JPEG/PNG RGB atau grayscale. Pilih grid 2×2 sampai 5×5 dan warna area tengah yang kosong.
2. Klik **Generate Puzzle**. Bingkai memakai empat strip dari sisi ujung foto asli: atas, bawah, kiri, dan kanan. Keempat sisi saling tersambung di sudut; bagian tengah kosong tanpa garis grid. Potongan ditampilkan acak.
3. Unduh bingkai PNG dan paket ZIP potongan. ZIP berisi `frame.png`, folder `pieces/`, serta `metadata.json`. Nama potongan acak dan tidak menyatakan posisinya.
4. Klik **Send to Puzzle Solver** agar paket langsung tersedia di halaman Solver, atau unggah bingkai dan ZIP secara terpisah.
5. Pilih **Auto Solve** untuk penyusunan tepat berdasarkan metadata. **Manual Arrange** memungkinkan memilih potongan untuk setiap sel. Tanpa metadata, gunakan Manual Arrange.
6. Unduh gambar rekonstruksi asli atau versi yang menampilkan kembali empat sisi tepi foto dari bingkai.

Gambar dengan dimensi yang tidak habis dibagi M ditangani tanpa membuang piksel; ukuran sebagian potongan dapat berbeda satu piksel. Mode warna RGB/grayscale dipertahankan. Aplikasi tidak mengirim gambar ke API eksternal.

## Struktur

- `app.py`: antarmuka Streamlit
- `generator.py`: bingkai, pemotongan, pengacakan, ZIP
- `solver.py`: validasi dan penyusunan kembali
- `image_utils.py`: pembacaan gambar dan metrik citra
- `styles.py`: gaya antarmuka
- `outputs/`: direktori output sementara bila diperlukan

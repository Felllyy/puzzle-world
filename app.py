"""Puzzle World Streamlit application."""
import hashlib
import math

import numpy as np
import streamlit as st

from generator import FRAME_COLORS, generate_puzzle
from image_utils import image_metrics, load_image, png_bytes
from solver import load_frame_and_pieces, solve_puzzle
from styles import CSS

st.set_page_config(page_title="Puzzle World", page_icon="🧩", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


def navigate(page):
    st.session_state.page = page
    st.rerun()


def section_header(kicker, title, description):
    st.markdown(f'<div class="pw-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.write(description)


with st.sidebar:
    st.markdown("## 🧩 Puzzle World")
    st.caption("Every Piece Finds Its Place")
    st.divider()
    pages = ["Dashboard", "Puzzle Generator", "Puzzle Solver", "About"]
    selected = st.radio("Menu", pages, index=pages.index(st.session_state.page),
                        label_visibility="collapsed")
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()
    st.divider()
    st.caption(f"Modul aktif: {st.session_state.page}")

page = st.session_state.page

if page == "Dashboard":
    st.markdown('''<div class="pw-hero"><div class="pw-label" style="color:#8ce8f1">WELCOME TO PUZZLE WORLD</div>
    <h1>Turn Your Photos Into Puzzles</h1><p>Ubah gambar menjadi potongan puzzle, lalu susun kembali dalam satu ruang kerja yang mudah digunakan.</p></div>''',
    unsafe_allow_html=True)
    st.write("")
    if st.button("Create New Puzzle →", type="primary"):
        navigate("Puzzle Generator")
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="pw-card"><h3>✂️ Puzzle Generator</h3><p>Unggah foto, tentukan grid, lalu buat bingkai dari empat sisi tepi foto.</p></div>', unsafe_allow_html=True)
        if st.button("Buka Generator", width="stretch"): navigate("Puzzle Generator")
    with right:
        st.markdown('<div class="pw-card"><h3>🧩 Puzzle Solver</h3><p>Susun otomatis dari metadata atau tempatkan potongan secara manual.</p></div>', unsafe_allow_html=True)
        if st.button("Buka Solver", width="stretch"): navigate("Puzzle Solver")
    st.subheader("Cara menggunakan")
    st.markdown("**1.** Unggah gambar dan buat puzzle.  **2.** Unduh ZIP berisi potongan dan metadata.  **3.** Kirim ke Solver atau unggah ZIP kembali untuk menyusun gambar.")

elif page == "Puzzle Generator":
    section_header("CREATE YOUR PUZZLE", "Puzzle Generator",
                   "Unggah gambar RGB atau grayscale. Bingkai memakai sisi ujung foto yang tersambung; bagian tengahnya kosong.")
    uploaded = st.file_uploader("Unggah gambar", type=["jpg", "jpeg", "png"], key="generator_upload")
    image = None
    if uploaded:
        try:
            image = load_image(uploaded.getvalue())
        except (ValueError, OSError) as exc:
            st.error(str(exc))
    if image:
        preview_col, control_col = st.columns([1.35, 1], gap="large")
        with preview_col:
            st.markdown('<div class="pw-label">ORIGINAL IMAGE</div>', unsafe_allow_html=True)
            st.image(image, width="stretch")
            metrics = image_metrics(image)
            st.caption(f'{metrics["width"]} × {metrics["height"]} px · {metrics["mode"]} · Kecerahan rata-rata {metrics["mean_brightness"]}')
        with control_col:
            st.markdown('<div class="pw-label">PUZZLE SETTINGS</div>', unsafe_allow_html=True)
            m = st.select_slider("Ukuran grid", options=[2, 3, 4, 5], value=3,
                                 format_func=lambda value: f"{value} × {value}")
            color = st.selectbox("Warna area tengah yang kosong", list(FRAME_COLORS), index=0)
            st.info(f"Puzzle akan menghasilkan {m * m} potongan PNG. Semua piksel gambar dipertahankan.")
            if st.button("Generate Puzzle", type="primary", width="stretch"):
                try:
                    result = generate_puzzle(image, m, color)
                    st.session_state.generated = result
                    st.session_state.generated_input = (hashlib.sha256(uploaded.getvalue()).hexdigest(), m, color)
                    st.success(f"Berhasil membuat {result['count']} potongan puzzle.")
                except (ValueError, OSError) as exc:
                    st.error(str(exc))
        result = st.session_state.get("generated")
        current_input = (hashlib.sha256(uploaded.getvalue()).hexdigest(), m, color)
        if result and st.session_state.get("generated_input") == current_input:
            st.divider()
            frame_col, pieces_col = st.columns([1, 1.2], gap="large")
            with frame_col:
                st.markdown('<div class="pw-label">PUZZLE FRAME</div>', unsafe_allow_html=True)
                st.image(result["frame"], width="stretch")
                st.caption("Empat sisi berasal dari tepi foto asli dan saling tersambung. Bagian tengah kosong tanpa garis grid.")
                st.download_button("Download Frame", png_bytes(result["frame"]),
                                   file_name="puzzle_frame.png", mime="image/png", width="stretch")
            with pieces_col:
                st.markdown('<div class="pw-label">PUZZLE PIECES</div>', unsafe_allow_html=True)
                st.metric("Jumlah potongan", result["count"])
                columns = st.columns(3)
                for index, piece in enumerate(result["pieces"]):
                    with columns[index % 3]:
                        st.image(piece["image"], caption=f"Piece {index + 1}", width="stretch")
                st.download_button("Download Pieces (ZIP)", result["package"],
                                   file_name="puzzle_world_pieces.zip", mime="application/zip",
                                   width="stretch", type="primary")
                if st.button("Send to Puzzle Solver →", width="stretch"):
                    st.session_state.sent_package = result["package"]
                    st.session_state.sent_frame = png_bytes(result["frame"])
                    navigate("Puzzle Solver")

elif page == "Puzzle Solver":
    section_header("PUT IT TOGETHER", "Puzzle Solver",
                   "Unggah bingkai dan potongan secara terpisah, atau gunakan ZIP dari Generator.")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="pw-label">INPUT 1 · PUZZLE FRAME</div>', unsafe_allow_html=True)
        frame_upload = st.file_uploader("Bingkai puzzle (PNG/JPG)", type=["png", "jpg", "jpeg"], key="solver_frame")
    with right:
        st.markdown('<div class="pw-label">INPUT 2 · PUZZLE PIECES</div>', unsafe_allow_html=True)
        zip_upload = st.file_uploader("ZIP potongan + metadata", type=["zip"], key="solver_zip")
        piece_uploads = st.file_uploader("Atau unggah beberapa gambar potongan", type=["png", "jpg", "jpeg"],
                                         accept_multiple_files=True, key="solver_pieces")
    sent_package = st.session_state.get("sent_package")
    sent_frame = st.session_state.get("sent_frame")
    if sent_package and not zip_upload:
        st.info("Paket dari Generator sudah diterima. Unggahan baru akan menggantikannya.")
    frame_bytes = frame_upload.getvalue() if frame_upload else sent_frame
    zip_bytes = zip_upload.getvalue() if zip_upload else sent_package
    uploads = [(item.name, item.getvalue()) for item in piece_uploads] if piece_uploads else []
    fingerprint = hashlib.sha256((frame_bytes or b"") + (zip_bytes or b"") +
                                 b"".join(name.encode() + data for name, data in uploads)).hexdigest()
    if st.session_state.get("solver_fingerprint") != fingerprint:
        st.session_state.solver_fingerprint = fingerprint
        st.session_state.pop("solved", None)
    frame = pieces = metadata = None
    if frame_bytes or zip_bytes or uploads:
        try:
            frame, pieces, metadata = load_frame_and_pieces(frame_bytes, uploads, zip_bytes)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            st.error(str(exc))
    if frame and pieces:
        preview_frame, preview_pieces = st.columns(2, gap="large")
        with preview_frame:
            st.markdown('<div class="pw-label">FRAME PREVIEW</div>', unsafe_allow_html=True)
            st.image(frame, width="stretch")
            st.caption(f"{frame.width} × {frame.height} px · {frame.mode}")
        with preview_pieces:
            st.markdown('<div class="pw-label">PIECES PREVIEW</div>', unsafe_allow_html=True)
            st.metric("Potongan terbaca", len(pieces))
            small_columns = st.columns(4)
            for index, (name, piece) in enumerate(pieces.items()):
                with small_columns[index % 4]:
                    st.image(piece, caption=name.split("/")[-1], width="stretch")
        mode = st.radio("Mode penyusunan", ["Auto Solve", "Manual Arrange"], horizontal=True,
                        disabled=not pieces)
        if mode == "Auto Solve":
            if metadata:
                st.success("Metadata posisi ditemukan. Auto Solve dapat menyusun potongan secara tepat.")
            else:
                st.warning("Metadata tidak tersedia. Posisi asli tidak dapat diketahui dengan pasti. Gunakan Manual Arrange.")
            manual_order = None
        else:
            count = len(pieces)
            m = math.isqrt(count)
            manual_order = []
            if m * m != count or m < 2:
                st.error("Jumlah potongan harus M × M dengan M minimal 2.")
            else:
                st.caption("Pilih satu potongan untuk setiap sel, dari kiri ke kanan dan atas ke bawah.")
                names = list(pieces)
                for row in range(m):
                    cells = st.columns(m)
                    for col in range(m):
                        index = row * m + col
                        with cells[col]:
                            manual_order.append(st.selectbox(f"Baris {row + 1}, Kolom {col + 1}",
                                                             names, index=index,
                                                             format_func=lambda value: value.split("/")[-1],
                                                             key=f"manual_{fingerprint}_{index}"))
        if st.button("Solve Puzzle", type="primary", width="stretch"):
            try:
                if mode == "Auto Solve" and not metadata:
                    raise ValueError("Metadata tidak tersedia. Pilih Manual Arrange.")
                with st.spinner("Menyusun potongan puzzle…"):
                    result, framed, status = solve_puzzle(frame, pieces, metadata,
                                                          manual_order if mode == "Manual Arrange" else None)
                st.session_state.solved = (result, framed, status)
                st.success(status)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                st.error(str(exc))
        if st.session_state.get("solved"):
            result, framed, status = st.session_state.solved
            st.divider()
            st.markdown('<div class="pw-label">SOLVED PUZZLE</div>', unsafe_allow_html=True)
            st.image(framed, caption="Hasil penyusunan dengan empat sisi tepi foto asli", width="stretch")
            st.success(status)
            st.download_button("Download Result", png_bytes(result), file_name="puzzle_solved.png",
                               mime="image/png", type="primary")
            st.download_button("Download Framed Result", png_bytes(framed),
                               file_name="puzzle_solved_framed.png", mime="image/png")
            generated = st.session_state.get("generated")
            if (generated and zip_bytes == generated["package"] and
                    generated["source"].size == result.size and generated["source"].mode == result.mode):
                exact = np.array_equal(np.asarray(generated["source"]), np.asarray(result))
                st.info("Perbandingan dengan gambar asli: " +
                        ("identik piksel demi piksel." if exact else "berbeda; periksa urutan potongan."))

else:
    section_header("ABOUT", "About Puzzle World",
                   "Aplikasi pembelajaran Pengolahan Citra Digital untuk membuat dan menyusun puzzle gambar.")
    st.markdown('''<div class="pw-card"><h3>Every Piece Finds Its Place</h3>
    <p>Generator mempertahankan semua piksel saat membagi gambar. Solver menggunakan metadata JSON untuk susunan otomatis yang tepat, atau pilihan pengguna untuk susunan manual.</p>
    <p>Teknologi: Python, Streamlit, Pillow, OpenCV, dan NumPy. Seluruh pemrosesan dilakukan secara lokal.</p></div>''',
    unsafe_allow_html=True)

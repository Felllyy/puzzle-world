"""Puzzle loading, validation, and reconstruction."""
from __future__ import annotations
from io import BytesIO
import json
import math
from pathlib import PurePosixPath
import zipfile

import numpy as np
from PIL import Image
from image_utils import frame_thickness, load_image

MAX_FILES = 100
MAX_UNCOMPRESSED = 120_000_000


def _safe_zip_entries(archive: zipfile.ZipFile):
    entries = archive.infolist()
    if len(entries) > MAX_FILES + 3 or sum(e.file_size for e in entries) > MAX_UNCOMPRESSED:
        raise ValueError("ZIP terlalu besar atau memuat terlalu banyak berkas.")
    for entry in entries:
        path = PurePosixPath(entry.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("ZIP memiliki lokasi berkas yang tidak aman.")
    return entries


def load_frame_and_pieces(frame_data: bytes | None, uploads: list[tuple[str, bytes]],
                          zip_data: bytes | None) -> tuple[Image.Image, dict[str, Image.Image], dict | None]:
    metadata = None
    pieces = {}
    packaged_frame = None
    if zip_data:
        try:
            with zipfile.ZipFile(BytesIO(zip_data)) as archive:
                entries = _safe_zip_entries(archive)
                names = {entry.filename for entry in entries}
                if "metadata.json" in names:
                    metadata = json.loads(archive.read("metadata.json"))
                if "frame.png" in names:
                    packaged_frame = load_image(archive.read("frame.png"))
                for name in names:
                    if name.startswith("pieces/") and name.lower().endswith(".png"):
                        pieces[name] = load_image(archive.read(name))
        except (zipfile.BadZipFile, RuntimeError) as exc:
            raise ValueError("ZIP puzzle tidak valid.") from exc
    for name, data in uploads:
        if name in pieces:
            raise ValueError(f"Nama potongan duplikat: {name}")
        pieces[name] = load_image(data)
    frame = load_image(frame_data) if frame_data else packaged_frame
    if frame is None:
        raise ValueError("Unggah bingkai puzzle atau gunakan ZIP dari Generator.")
    if not pieces:
        raise ValueError("Unggah potongan puzzle atau ZIP dari Generator.")
    return frame, pieces, metadata


def reconstruct_image(frame: Image.Image, pieces: dict[str, Image.Image],
                      placements: list[dict], width: int, height: int) -> Image.Image:
    if frame.size != (width, height):
        raise ValueError("Ukuran bingkai tidak sesuai dengan puzzle.")
    if any(piece.mode != frame.mode for piece in pieces.values()):
        raise ValueError("Mode warna bingkai dan potongan harus sama.")
    canvas = Image.new(frame.mode, (width, height))
    occupied = set()
    for entry in placements:
        name = entry["file"]
        if name not in pieces or name in occupied:
            raise ValueError("Potongan hilang atau digunakan lebih dari sekali.")
        occupied.add(name)
        x0, y0, x1, y1 = map(int, entry["box"])
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError("Koordinat potongan tidak valid.")
        if pieces[name].size != (x1 - x0, y1 - y0):
            raise ValueError(f"Ukuran potongan tidak cocok: {name}")
        canvas.paste(pieces[name], (x0, y0))
    if len(occupied) != len(pieces):
        raise ValueError("Ada potongan yang tidak digunakan.")
    return canvas


def solve_puzzle(frame: Image.Image, pieces: dict[str, Image.Image],
                 metadata: dict | None = None,
                 manual_order: list[str] | None = None) -> tuple[Image.Image, Image.Image, str]:
    count = len(pieces)
    m = math.isqrt(count)
    if m * m != count or m < 2:
        raise ValueError(f"Jumlah potongan harus M² (minimal 4); ditemukan {count}.")
    if metadata is not None and manual_order is None:
        if metadata.get("schema") != "puzzle-world-1" or metadata.get("M") != m:
            raise ValueError("Metadata puzzle tidak sesuai.")
        entries = metadata.get("pieces", [])
        if len(entries) != count or {e["file"] for e in entries} != set(pieces):
            raise ValueError("Metadata dan berkas potongan tidak cocok.")
        positions = {(e["row"], e["column"]) for e in entries}
        if positions != {(row, col) for row in range(m) for col in range(m)}:
            raise ValueError("Posisi potongan pada metadata tidak lengkap.")
        width, height = int(metadata["width"]), int(metadata["height"])
        if metadata.get("mode") != frame.mode:
            raise ValueError("Mode warna metadata dan bingkai tidak cocok.")
        for entry in entries:
            row, col = entry["row"], entry["column"]
            expected = [col * width // m, row * height // m,
                        (col + 1) * width // m, (row + 1) * height // m]
            if entry["box"] != expected:
                raise ValueError("Koordinat potongan pada metadata tidak sesuai grid.")
        result = reconstruct_image(frame, pieces, entries,
                                   width, height)
        status = "Berhasil: semua potongan disusun dari metadata Generator."
    elif manual_order is not None:
        if len(manual_order) != count or set(manual_order) != set(pieces):
            raise ValueError("Setiap potongan harus dipilih tepat satu kali.")
        widths = []
        for col in range(m):
            col_widths = {pieces[manual_order[row * m + col]].width for row in range(m)}
            if len(col_widths) != 1:
                raise ValueError("Lebar potongan pada kolom yang sama harus seragam.")
            widths.append(col_widths.pop())
        heights = []
        for row in range(m):
            row_heights = {pieces[manual_order[row * m + col]].height for col in range(m)}
            if len(row_heights) != 1:
                raise ValueError("Tinggi potongan pada baris yang sama harus seragam.")
            heights.append(row_heights.pop())
        if sum(widths) != frame.width or sum(heights) != frame.height:
            raise ValueError("Total ukuran potongan tidak sesuai dengan bingkai.")
        xs = [0]
        ys = [0]
        for width in widths: xs.append(xs[-1] + width)
        for height in heights: ys.append(ys[-1] + height)
        entries = [{"file": manual_order[row * m + col],
                    "box": [xs[col], ys[row], xs[col + 1], ys[row + 1]]}
                   for row in range(m) for col in range(m)]
        result = reconstruct_image(frame, pieces, entries, frame.width, frame.height)
        status = "Selesai: gambar disusun sesuai pilihan manual Anda."
    else:
        raise ValueError("Metadata tidak tersedia. Gunakan Manual Arrange untuk menentukan posisi potongan.")
    thickness = frame_thickness(frame.width, frame.height)
    if metadata is not None and manual_order is None:
        original = np.asarray(result)
        border = np.asarray(frame)
        same_edges = (np.array_equal(original[:thickness], border[:thickness]) and
                      np.array_equal(original[-thickness:], border[-thickness:]) and
                      np.array_equal(original[:, :thickness], border[:, :thickness]) and
                      np.array_equal(original[:, -thickness:], border[:, -thickness:]))
        if not same_edges:
            raise ValueError("Sisi bingkai tidak cocok dengan potongan gambar.")
    framed = result.copy()
    framed.paste(frame.crop((0, 0, frame.width, thickness)), (0, 0))
    framed.paste(frame.crop((0, frame.height - thickness, frame.width, frame.height)),
                 (0, frame.height - thickness))
    framed.paste(frame.crop((0, 0, thickness, frame.height)), (0, 0))
    framed.paste(frame.crop((frame.width - thickness, 0, frame.width, frame.height)),
                 (frame.width - thickness, 0))
    return result, framed, status

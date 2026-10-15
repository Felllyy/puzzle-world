"""Puzzle frame and piece generation."""
from io import BytesIO
import json
import secrets
import random
import zipfile

import numpy as np
from PIL import Image

from image_utils import frame_thickness, png_bytes

FRAME_COLORS = {
    "Putih": (255, 255, 255), "Hitam": (24, 28, 43),
    "Biru tua": (36, 48, 105), "Hijau": (27, 125, 96),
}


def create_frame(image: Image.Image, color: str = "Biru tua") -> Image.Image:
    if color not in FRAME_COLORS:
        raise ValueError("Warna area kosong tidak dikenal.")
    width, height = image.size
    if min(width, height) < 3:
        raise ValueError("Gambar terlalu kecil untuk bingkai.")
    thickness = frame_thickness(width, height)
    canvas = np.asarray(image).copy()
    background = FRAME_COLORS[color] if image.mode == "RGB" else int(round(sum(FRAME_COLORS[color]) / 3))
    canvas[thickness:height - thickness, thickness:width - thickness] = background
    return Image.fromarray(canvas)


def split_image(image: Image.Image, m: int) -> list[dict]:
    if not isinstance(m, int) or m < 2 or m > 10 or m > min(image.size):
        raise ValueError("M harus 2–10 dan tidak boleh melebihi dimensi gambar.")
    xs = [i * image.width // m for i in range(m + 1)]
    ys = [i * image.height // m for i in range(m + 1)]
    return [{"image": image.crop((xs[col], ys[row], xs[col + 1], ys[row + 1])),
             "row": row, "column": col,
             "box": [xs[col], ys[row], xs[col + 1], ys[row + 1]]}
            for row in range(m) for col in range(m)]


def shuffle_pieces(pieces: list[dict]) -> list[dict]:
    shuffled = list(pieces)
    random.SystemRandom().shuffle(shuffled)
    return shuffled


def save_pieces(pieces: list[dict], image: Image.Image, m: int,
                frame: Image.Image) -> tuple[bytes, dict, list[dict]]:
    """Create an opaque-named ZIP and position metadata."""
    shuffled = shuffle_pieces(pieces)
    metadata = {"schema": "puzzle-world-1", "width": image.width,
                "height": image.height, "mode": image.mode, "M": m, "pieces": []}
    display = []
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("frame.png", png_bytes(frame))
        for index, piece in enumerate(shuffled, 1):
            name = f"piece_{index:03d}_{secrets.token_hex(3)}.png"
            archive.writestr(f"pieces/{name}", png_bytes(piece["image"]))
            metadata["pieces"].append({"file": f"pieces/{name}",
                                       "row": piece["row"], "column": piece["column"],
                                       "box": piece["box"]})
            display.append({"name": name, "image": piece["image"]})
        archive.writestr("metadata.json", json.dumps(metadata, indent=2))
    return stream.getvalue(), metadata, display


def generate_puzzle(image: Image.Image, m: int, color: str) -> dict:
    frame = create_frame(image, color)
    pieces = split_image(image, m)
    package, metadata, display = save_pieces(pieces, image, m, frame)
    return {"frame": frame, "pieces": display, "metadata": metadata,
            "package": package, "count": len(display), "source": image}

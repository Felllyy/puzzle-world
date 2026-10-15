"""Shared image loading and inspection helpers."""
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import cv2
import numpy as np


def load_image(data: bytes) -> Image.Image:
    try:
        with Image.open(BytesIO(data)) as source:
            source.load()
            if source.mode not in ("RGB", "L"):
                raise ValueError("Gunakan gambar RGB atau grayscale 8-bit.")
            return source.copy()
    except UnidentifiedImageError as exc:
        raise ValueError("Berkas bukan gambar yang didukung.") from exc


def png_bytes(image: Image.Image) -> bytes:
    stream = BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def frame_thickness(width: int, height: int) -> int:
    """Width of the four photo-edge strips, leaving a nonempty center."""
    return max(1, min(80, min(width, height) // 8))


def image_metrics(image: Image.Image) -> dict:
    """Simple PCD measurements using NumPy and OpenCV."""
    array = np.asarray(image)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY) if image.mode == "RGB" else array
    edges = cv2.Canny(gray, 80, 160)
    return {"width": image.width, "height": image.height,
            "mode": image.mode, "mean_brightness": round(float(np.mean(gray)), 1),
            "edge_pixels": int(np.count_nonzero(edges))}

import io
import base64
from PIL import Image
import requests

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920  # 9:16


def fetch_and_crop(image_url: str) -> bytes:
    """Download an image, crop/resize to 9:16, return JPEG bytes."""
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    return _process_bytes(response.content)


def process_local_file(file_path: str) -> bytes:
    """Process a local image file to 9:16 JPEG bytes."""
    with open(file_path, "rb") as f:
        return _process_bytes(f.read())


def to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def _process_bytes(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data))

    if img.mode != "RGB":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img)
        img = bg

    img = _smart_crop(img)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()


def _smart_crop(img: Image.Image) -> Image.Image:
    """Center-crop to 9:16 then resize to 1080×1920."""
    orig_w, orig_h = img.size
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT  # 0.5625

    if orig_w / orig_h > target_ratio:
        # Wider than 9:16 → crop the sides
        new_w = int(orig_h * target_ratio)
        left = (orig_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, orig_h))
    else:
        # Taller than 9:16 → crop top/bottom, keep upper 60% (subjects usually top)
        new_h = int(orig_w / target_ratio)
        top = int((orig_h - new_h) * 0.35)
        top = max(0, min(top, orig_h - new_h))
        img = img.crop((0, top, orig_w, top + new_h))

    return img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

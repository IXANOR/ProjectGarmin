import io

import pytest
import httpx
from PIL import Image, ImageDraw

from app.main import app


def _png_bytes(text: str) -> bytes:
    img = Image.new("RGB", (200, 80), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 30), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_images_api_upload_list_delete_flow(monkeypatch):
    # Make OCR deterministic and independent from tesseract binary
    from app.services import ocr as ocr_module
    monkeypatch.setattr(ocr_module.pytesseract, "image_to_string", lambda img, lang=None: "text detected from image")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        sess = await client.post("/api/sessions", json={"name": "For Images"})
        assert sess.status_code == 201
        session_id = sess.json()["id"]

        # Upload valid image for session
        img_bytes = _png_bytes("Hello")
        files = {"file": ("photo.png", img_bytes, "image/png")}
        data = {"session_id": session_id}
        up = await client.post("/api/images", files=files, data=data)
        assert up.status_code == 201
        rec = up.json()
        assert rec["name"] == "photo.png"
        assert rec["session_id"] == session_id
        image_id = rec["id"]

        # Upload global image
        img_bytes2 = _png_bytes("World")
        files2 = {"file": ("global.png", img_bytes2, "image/png")}
        up2 = await client.post("/api/images", files=files2)
        assert up2.status_code == 201
        rec2 = up2.json()
        assert rec2["session_id"] is None

        # List by session should include both
        lst = await client.get(f"/api/images", params={"session_id": session_id})
        assert lst.status_code == 200
        ids = {i["id"] for i in lst.json()}
        assert image_id in ids and rec2["id"] in ids

        # Delete first image
        delr = await client.delete(f"/api/images/{image_id}")
        assert delr.status_code == 204

        # Ensure it's gone
        lst2 = await client.get(f"/api/images", params={"session_id": session_id})
        assert all(i["id"] != image_id for i in lst2.json())


@pytest.mark.asyncio
async def test_images_api_rejects_unsupported_format():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("not-image.txt", b"hello", "text/plain")}
        resp = await client.post("/api/images", files=files)
        assert resp.status_code == 400
        assert "Unsupported" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_images_api_rejects_too_large(monkeypatch):
    # Set a low max size
    monkeypatch.setenv("IMAGES_MAX_FILE_SIZE_MB", "0.0001")  # ~100 bytes
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Make a slightly larger image
        img = Image.new("RGB", (200, 200), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()
        files = {"file": ("big.png", data, "image/png")}
        resp = await client.post("/api/images", files=files)
        assert resp.status_code == 400
        assert "large" in resp.json().get("detail", "").lower()



import io
import uuid

import pytest
import httpx
from fpdf import FPDF

from app.main import app


def _pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, text=line)
    return bytes(pdf.output(dest="S"))


@pytest.mark.asyncio
async def test_files_api_upload_list_delete_flow(tmp_path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session; also allow global upload later
        sess_resp = await client.post("/api/sessions", json={"name": "For Files"})
        assert sess_resp.status_code == 201
        session_id = sess_resp.json()["id"]

        # Upload valid PDF for session
        text = "Session-linked PDF content for RAG test."
        pdf_bytes = _pdf_bytes(text)
        files = {"file": ("doc1.pdf", pdf_bytes, "application/pdf")}
        data = {"session_id": session_id}
        up = await client.post("/api/files", files=files, data=data)
        assert up.status_code == 201
        file_record = up.json()
        assert file_record["name"] == "doc1.pdf"
        assert file_record["session_id"] == session_id
        assert file_record["size_bytes"] > 0
        file_id = file_record["id"]

        # Upload a global file (no session_id)
        pdf_bytes2 = _pdf_bytes("Global content")
        files2 = {"file": ("global.pdf", pdf_bytes2, "application/pdf")}
        up2 = await client.post("/api/files", files=files2)
        assert up2.status_code == 201
        file2 = up2.json()
        assert file2["session_id"] is None

        # List for session: should include both session-specific and global
        lst = await client.get(f"/api/files", params={"session_id": session_id})
        assert lst.status_code == 200
        items = lst.json()
        ids = {i["id"] for i in items}
        assert file_id in ids and file2["id"] in ids

        # List all
        lst_all = await client.get("/api/files")
        assert lst_all.status_code == 200
        assert len(lst_all.json()) >= 2

        # Delete first file
        del_resp = await client.delete(f"/api/files/{file_id}")
        assert del_resp.status_code == 204

        # Ensure it's gone from list
        lst2 = await client.get(f"/api/files", params={"session_id": session_id})
        assert all(i["id"] != file_id for i in lst2.json())


@pytest.mark.asyncio
async def test_files_api_rejects_non_pdf():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("not.pdf", b"hello", "text/plain")}
        resp = await client.post("/api/files", files=files)
        assert resp.status_code == 400
        assert "PDF" in resp.json().get("detail", "")



"""Text extraction with simple size guards."""
from io import BytesIO
from pypdf import PdfReader

MAX_BYTES = 5 * 1024 * 1024
MAX_CHARS = 15000


def extract_text(name: str, data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise ValueError("File exceeds 5 MB limit")
    if name.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages[:30])
    elif name.lower().endswith(".txt"):
        text = data.decode("utf-8-sig")
    else:
        raise ValueError("Only TXT and text-based PDF files are supported")
    text = text.strip()
    if not text:
        raise ValueError("No readable text found. Scanned PDFs need OCR and are not supported.")
    return text[:MAX_CHARS]

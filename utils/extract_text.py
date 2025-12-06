# utils/extract_text.py

import io
from typing import List

from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file_like: io.BytesIO) -> str:
    reader = PdfReader(file_like)
    texts: List[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def extract_text_from_docx(file_like: io.BytesIO) -> str:
    doc = Document(file_like)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_txt(file_like: io.BytesIO) -> str:
    content = file_like.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="ignore")


def extract_text_any(file_name: str, file_like: io.BytesIO) -> str:
    file_name_l = file_name.lower()
    file_like.seek(0)

    if file_name_l.endswith(".pdf"):
        return extract_text_from_pdf(file_like)
    elif file_name_l.endswith(".docx"):
        return extract_text_from_docx(file_like)
    elif file_name_l.endswith(".txt"):
        return extract_text_from_txt(file_like)
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

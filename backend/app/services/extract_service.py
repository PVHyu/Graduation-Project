from pathlib import Path

import fitz
from docx import Document
from fastapi import HTTPException, status

from app.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS


def extract_text_from_txt(file_path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "latin-1"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Không thể đọc file TXT do lỗi mã hóa."
    )


def extract_text_from_docx(file_path: Path) -> str:
    try:
        document = Document(file_path)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể đọc nội dung file DOCX."
        )


def extract_text_from_pdf(file_path: Path) -> str:
    try:
        doc = fitz.open(file_path)
        text_parts = []

        for page in doc:
            text_parts.append(page.get_text("text"))

        doc.close()
        return "\n".join(text_parts)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể đọc nội dung file PDF."
        )


def extract_text_by_filename(saved_filename: str) -> dict:
    if not saved_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên file không hợp lệ."
        )

    file_path = UPLOAD_DIR / saved_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy file đã upload."
        )

    extension = file_path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng file không được hỗ trợ."
        )

    if extension == ".txt":
        extracted_text = extract_text_from_txt(file_path)
    elif extension == ".docx":
        extracted_text = extract_text_from_docx(file_path)
    elif extension == ".pdf":
        extracted_text = extract_text_from_pdf(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không hỗ trợ loại file này."
        )

    return {
        "saved_filename": saved_filename,
        "extension": extension,
        "extracted_text": extracted_text,
        "char_count": len(extracted_text),
        "message": "Trích xuất văn bản thành công."
    }
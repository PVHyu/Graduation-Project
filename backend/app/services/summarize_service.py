import re
from fastapi import HTTPException, status

from app.core.config import MAX_CHUNK_CHARS
from app.services.ai_service import call_ai_json
from app.services.clean_service import clean_text_by_filename


def split_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def split_text_into_chunks(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    paragraphs = split_paragraphs(text)

    if not paragraphs:
        return [text.strip()] if text.strip() else []

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = f"{current_chunk}\n\n{paragraph}".strip() if current_chunk else paragraph

        if len(candidate) <= max_chars:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)

            if len(paragraph) <= max_chars:
                current_chunk = paragraph
            else:
                start = 0
                while start < len(paragraph):
                    end = start + max_chars
                    piece = paragraph[start:end].strip()
                    if piece:
                        chunks.append(piece)
                    start = end
                current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def build_chunk_prompt(chunk_text: str) -> str:
    return f"""
Bạn là hệ thống tóm tắt tài liệu học thuật bằng tiếng Việt.

Nhiệm vụ:
- Đọc đoạn văn bản được cung cấp.
- Tạo bản tóm tắt ngắn gọn, rõ ràng, trung lập.
- Trích ra các ý chính quan trọng nhất.

Yêu cầu:
- Không bịa thông tin ngoài văn bản.
- Giữ đúng ngữ cảnh tài liệu.
- Tóm tắt bằng tiếng Việt.
- Trả về đúng JSON với cấu trúc:

{{
  "summary": "string",
  "main_points": ["string", "string", "string"]
}}

Văn bản:
{chunk_text}
""".strip()


def build_reduce_prompt(partial_results: list[dict]) -> str:
    partial_text = "\n\n".join(
        [
            f"Phần {i + 1}:\n"
            f"- Summary: {item['summary']}\n"
            f"- Main points: {', '.join(item['main_points'])}"
            for i, item in enumerate(partial_results)
        ]
    )

    return f"""
Bạn là hệ thống tổng hợp tóm tắt tài liệu.

Dưới đây là các bản tóm tắt con của từng phần trong tài liệu.
Hãy tổng hợp lại thành:
- một bản tóm tắt chung ngắn gọn
- danh sách các ý chính quan trọng nhất

Yêu cầu:
- Không lặp ý
- Không bịa thêm thông tin
- Dùng tiếng Việt
- Trả về đúng JSON:

{{
  "summary": "string",
  "main_points": ["string", "string", "string", "string"]
}}

Dữ liệu đầu vào:
{partial_text}
""".strip()


def validate_ai_result(data: dict) -> dict:
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI trả về dữ liệu không hợp lệ."
        )

    summary = data.get("summary")
    main_points = data.get("main_points")

    if not isinstance(summary, str) or not summary.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI không trả về summary hợp lệ."
        )

    if not isinstance(main_points, list) or not main_points:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI không trả về main_points hợp lệ."
        )

    normalized_points = [
        str(point).strip()
        for point in main_points
        if str(point).strip()
    ]

    if not normalized_points:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Danh sách main_points rỗng sau khi chuẩn hóa."
        )

    return {
        "summary": summary.strip(),
        "main_points": normalized_points[:5]
    }


def summarize_text_by_filename(saved_filename: str) -> dict:
    cleaned = clean_text_by_filename(saved_filename)
    clean_text = cleaned["clean_text"].strip()

    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có nội dung sạch để tóm tắt."
        )

    chunks = split_text_into_chunks(clean_text)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể chia văn bản thành chunk hợp lệ."
        )

    partial_results = []

    for chunk in chunks:
        prompt = build_chunk_prompt(chunk)
        ai_result = call_ai_json(prompt)
        validated = validate_ai_result(ai_result)
        partial_results.append(validated)

    if len(partial_results) == 1:
        final_result = partial_results[0]
    else:
        reduce_prompt = build_reduce_prompt(partial_results)
        reduced_result = call_ai_json(reduce_prompt)
        final_result = validate_ai_result(reduced_result)

    return {
        "saved_filename": saved_filename,
        "summary": final_result["summary"],
        "main_points": final_result["main_points"],
        "chunks_count": len(chunks),
        "message": "Tóm tắt bằng AI thành công."
    }
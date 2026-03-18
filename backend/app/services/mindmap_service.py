from fastapi import HTTPException, status

from app.core.config import (
    MAX_MINDMAP_CHILDREN,
    MAX_MINDMAP_DEPTH,
    MINDMAP_SOURCE_PREVIEW_CHARS,
)
from app.services.ai_service import call_ai_raw_json
from app.services.clean_service import clean_text_by_filename
from app.services.summarize_service import summarize_text_by_filename


def truncate_text(text: str, max_length: int = 80) -> str:
    text = str(text).strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].strip() + "..."


def build_mindmap_prompt(summary: str, main_points: list[str], source_preview: str) -> str:
    main_points_text = "\n".join([f"- {point}" for point in main_points])

    return f"""
Bạn là hệ thống tạo sơ đồ tư duy cho tài liệu tiếng Việt.

Nhiệm vụ:
- Dựa trên bản tóm tắt, danh sách ý chính và trích đoạn nội dung tài liệu
- Tạo sơ đồ tư duy dạng cây

Yêu cầu:
- Trả về DUY NHẤT JSON
- Không thêm giải thích ngoài JSON
- Dùng tiếng Việt
- Không bịa thông tin ngoài dữ liệu đầu vào
- Dùng cụm ý ngắn gọn, không dùng câu quá dài
- Chủ đề trung tâm phải ngắn gọn
- Có 3 đến 6 nhánh chính
- Mỗi nhánh chính có 1 đến 4 nhánh phụ nếu phù hợp
- Mỗi title nên ngắn gọn, ưu tiên cụm từ thay vì câu dài

JSON bắt buộc đúng cấu trúc:
{{
  "title": "string",
  "children": [
    {{
      "title": "string",
      "children": [
        {{
          "title": "string",
          "children": []
        }}
      ]
    }}
  ]
}}

Bản tóm tắt:
{summary}

Danh sách ý chính:
{main_points_text}

Trích đoạn nội dung:
{source_preview}
""".strip()


def normalize_mindmap_node(node: dict, depth: int = 0) -> dict:
    if not isinstance(node, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Node mind map không đúng định dạng object."
        )

    title = str(node.get("title", "")).strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mind map có node thiếu title."
        )

    title = truncate_text(title, 100)

    if depth >= MAX_MINDMAP_DEPTH:
        return {
            "title": title,
            "children": []
        }

    children = node.get("children", [])
    if not isinstance(children, list):
        children = []

    normalized_children = []
    for child in children[:MAX_MINDMAP_CHILDREN]:
        try:
            normalized_child = normalize_mindmap_node(child, depth + 1)
            normalized_children.append(normalized_child)
        except HTTPException:
            continue

    return {
        "title": title,
        "children": normalized_children
    }


def validate_final_mindmap(tree: dict) -> dict:
    normalized = normalize_mindmap_node(tree, depth=0)

    if not normalized.get("children"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mind map không có nhánh chính hợp lệ."
        )

    return normalized


def generate_mindmap_by_filename(saved_filename: str) -> dict:
    cleaned = clean_text_by_filename(saved_filename)
    summarized = summarize_text_by_filename(saved_filename)

    clean_text = cleaned["clean_text"].strip()
    summary = summarized["summary"]
    main_points = summarized["main_points"]

    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có nội dung sạch để sinh mind map."
        )

    source_preview = clean_text[:MINDMAP_SOURCE_PREVIEW_CHARS]

    prompt = build_mindmap_prompt(
        summary=summary,
        main_points=main_points,
        source_preview=source_preview
    )

    raw_tree = call_ai_raw_json(prompt)
    mindmap = validate_final_mindmap(raw_tree)

    return {
        "saved_filename": saved_filename,
        "summary": summary,
        "main_points": main_points,
        "mindmap": mindmap,
        "message": "Sinh sơ đồ tư duy bằng AI thành công."
    }
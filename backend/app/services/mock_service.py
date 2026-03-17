import re

from app.services.clean_service import clean_text_by_filename


def truncate_text(text: str, max_length: int = 120) -> str:
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].strip() + "..."


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def extract_topic(clean_text: str) -> str:
    paragraphs = split_paragraphs(clean_text)
    if paragraphs:
        first = paragraphs[0].replace("\n", " ").strip()
        return truncate_text(first, 80)
    return "Chủ đề tài liệu"


def generate_fake_summary(clean_text: str) -> str:
    sentences = split_sentences(clean_text)

    if len(sentences) >= 3:
        return " ".join(sentences[:3])

    if len(sentences) > 0:
        return " ".join(sentences)

    return truncate_text(clean_text, 300) or "Chưa có nội dung để tóm tắt."


def generate_fake_main_points(clean_text: str) -> list[str]:
    paragraphs = split_paragraphs(clean_text)
    points = []

    for paragraph in paragraphs[:3]:
        sentences = split_sentences(paragraph)
        if sentences:
            points.append(truncate_text(sentences[0], 120))
        else:
            points.append(truncate_text(paragraph, 120))

    if not points:
        points = [
            "Nội dung chính của tài liệu",
            "Các ý quan trọng cần chú ý",
            "Kết luận hoặc định hướng triển khai"
        ]

    return points[:3]


def generate_fake_mindmap(clean_text: str, main_points: list[str]) -> dict:
    paragraphs = split_paragraphs(clean_text)
    topic = extract_topic(clean_text)

    children = []

    for index, point in enumerate(main_points):
        branch_children = []

        if index < len(paragraphs):
            sentences = split_sentences(paragraphs[index])
            for sentence in sentences[1:3]:
                branch_children.append({
                    "title": truncate_text(sentence, 80),
                    "children": []
                })

        if not branch_children:
            branch_children = [
                {"title": "Nội dung chi tiết 1", "children": []},
                {"title": "Nội dung chi tiết 2", "children": []}
            ]

        children.append({
            "title": point,
            "children": branch_children
        })

    return {
        "title": topic,
        "children": children
    }


def generate_mock_result(saved_filename: str) -> dict:
    cleaned = clean_text_by_filename(saved_filename)
    clean_text = cleaned["clean_text"]

    summary = generate_fake_summary(clean_text)
    main_points = generate_fake_main_points(clean_text)
    mindmap = generate_fake_mindmap(clean_text, main_points)

    return {
        "saved_filename": saved_filename,
        "summary": summary,
        "main_points": main_points,
        "mindmap": mindmap,
        "clean_text_preview": truncate_text(clean_text, 500),
        "message": "Sinh dữ liệu giả thành công."
    }
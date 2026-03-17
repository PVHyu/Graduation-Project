import re

from app.services.extract_service import extract_text_by_filename


def remove_control_characters(text: str) -> str:
    """
    Loại bỏ ký tự điều khiển, nhưng vẫn giữ \n và \t ở mức cần thiết.
    """
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
    return text


def normalize_line_endings(text: str) -> str:
    """
    Chuẩn hóa xuống dòng về dạng \n.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def normalize_spaces(text: str) -> str:
    """
    Chuẩn hóa khoảng trắng:
    - đổi tab thành space
    - gộp nhiều space liên tiếp thành 1 space
    - xóa space thừa ở đầu/cuối dòng
    """
    text = text.replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text


def remove_empty_noise_lines(text: str) -> str:
    """
    Loại bỏ các dòng quá ngắn hoặc chỉ toàn ký hiệu ngăn cách.
    Ví dụ: ----- hoặc _______
    """
    cleaned_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        if re.fullmatch(r"[-_=~*]{3,}", stripped):
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def merge_broken_lines(text: str) -> str:
    """
    Ghép các dòng bị ngắt sai trong cùng một đoạn.
    Ý tưởng:
    - Nếu dòng trước và dòng sau đều có nội dung
    - Và không có dấu kết thúc câu mạnh ở cuối dòng trước
    - Thì ghép lại bằng khoảng trắng
    - Nếu có dòng trống, coi như ngắt đoạn
    """
    lines = text.split("\n")
    merged_paragraphs = []
    current_paragraph = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if current_paragraph:
                merged_paragraphs.append(" ".join(current_paragraph).strip())
                current_paragraph = []
            continue

        if not current_paragraph:
            current_paragraph.append(stripped)
            continue

        previous_line = current_paragraph[-1]

        if re.search(r"[.!?:;]$", previous_line):
            merged_paragraphs.append(" ".join(current_paragraph).strip())
            current_paragraph = [stripped]
        else:
            current_paragraph.append(stripped)

    if current_paragraph:
        merged_paragraphs.append(" ".join(current_paragraph).strip())

    return "\n\n".join(merged_paragraphs)


def clean_extracted_text(raw_text: str) -> str:
    text = raw_text

    text = normalize_line_endings(text)
    text = remove_control_characters(text)
    text = normalize_spaces(text)
    text = remove_empty_noise_lines(text)
    text = merge_broken_lines(text)

    # Gộp quá nhiều dòng trống thành tối đa 2 dòng
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Xóa khoảng trắng thừa lần cuối
    text = text.strip()

    return text


def clean_text_by_filename(saved_filename: str) -> dict:
    extracted = extract_text_by_filename(saved_filename)

    raw_text = extracted["extracted_text"]
    clean_text = clean_extracted_text(raw_text)

    return {
        "saved_filename": extracted["saved_filename"],
        "extension": extracted["extension"],
        "raw_text": raw_text,
        "clean_text": clean_text,
        "raw_char_count": len(raw_text),
        "clean_char_count": len(clean_text),
        "message": "Làm sạch văn bản thành công."
    }   
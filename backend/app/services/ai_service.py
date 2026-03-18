import json
import os
import re
from typing import Any
from urllib import error, request

from fastapi import HTTPException, status

from app.core.config import AI_MODEL

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
DEFAULT_MODEL = AI_MODEL or "qwen3:4b"
REQUEST_TIMEOUT_SECONDS = 600


def _strip_code_fences(text: str) -> str:
    """
    Xóa markdown code fence nếu model trả kiểu:
    ```json
    {...}
    ```
    """
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    return text


def _extract_first_json_block(text: str) -> str:
    """
    Nếu model trả thêm lời giải thích ngoài JSON,
    cố gắng lấy block JSON đầu tiên.
    """
    text = _strip_code_fences(text)

    # Thử parse trực tiếp trước
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Tìm object JSON đầu tiên
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        candidate = match.group(0).strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="AI có phản hồi nhưng không chứa JSON hợp lệ."
    )


def _normalize_result(data: dict[str, Any]) -> dict[str, Any]:
    """
    Chuẩn hóa kết quả để summarize_service.py dùng ổn định.
    """
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dữ liệu AI trả về không phải object JSON."
        )

    summary = data.get("summary", "")
    main_points = data.get("main_points", [])

    if not isinstance(summary, str):
        summary = str(summary)

    if not isinstance(main_points, list):
        main_points = [str(main_points)]

    normalized_points = []
    for point in main_points:
        point_str = str(point).strip()
        if point_str:
            normalized_points.append(point_str)

    summary = summary.strip()

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI không trả về summary hợp lệ."
        )

    if not normalized_points:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI không trả về main_points hợp lệ."
        )

    return {
        "summary": summary,
        "main_points": normalized_points[:5]
    }


def _post_to_ollama(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Gửi request tới Ollama local API.
    """
    url = f"{OLLAMA_BASE_URL}/chat"

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            response_bytes = resp.read()
            response_text = response_bytes.decode("utf-8")
            return json.loads(response_text)

    except error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            error_body = ""

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ollama HTTPError {e.code}: {error_body or e.reason}"
        )

    except error.URLError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không kết nối được tới Ollama. "
                "Hãy kiểm tra Ollama đã chạy chưa và base URL có đúng không."
            )
        )

    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hết thời gian chờ phản hồi từ Ollama."
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Phản hồi từ Ollama không phải JSON hợp lệ."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi không xác định khi gọi Ollama: {str(e)}"
        )


def call_ai_json(prompt: str) -> dict[str, Any]:
    """
    Hàm chính được summarize_service.py gọi.

    Đầu vào:
        prompt: prompt đã build sẵn từ summarize_service.py

    Đầu ra mong muốn:
        {
            "summary": "...",
            "main_points": ["...", "..."]
        }
    """
    if not prompt or not prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt gửi tới AI đang rỗng."
        )

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt.strip()
            }
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {
            "temperature": 0.2
        }
    }

    ollama_response = _post_to_ollama(payload)

    message = ollama_response.get("message")
    if not isinstance(message, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ollama không trả về trường message hợp lệ."
        )

    content = message.get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ollama không trả về nội dung hợp lệ trong message.content."
        )

    json_text = _extract_first_json_block(content)

    try:
        parsed = json.loads(json_text)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không parse được JSON từ nội dung AI trả về."
        )

    return _normalize_result(parsed)
from pydantic import BaseModel


class UploadResponse(BaseModel):
    original_filename: str
    saved_filename: str
    extension: str
    content_type: str | None
    size: int
    message: str
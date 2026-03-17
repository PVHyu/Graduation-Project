from pydantic import BaseModel


class ExtractRequest(BaseModel):
    saved_filename: str


class ExtractResponse(BaseModel):
    saved_filename: str
    extension: str
    extracted_text: str
    char_count: int
    message: str
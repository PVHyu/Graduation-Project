from pydantic import BaseModel


class CleanRequest(BaseModel):
    saved_filename: str


class CleanResponse(BaseModel):
    saved_filename: str
    extension: str
    raw_text: str
    clean_text: str
    raw_char_count: int
    clean_char_count: int
    message: str
from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    saved_filename: str


class SummarizeResponse(BaseModel):
    saved_filename: str
    summary: str
    main_points: list[str]
    chunks_count: int
    message: str
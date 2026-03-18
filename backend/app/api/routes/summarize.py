from fastapi import APIRouter

from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.summarize_service import summarize_text_by_filename

router = APIRouter()


@router.post("/", response_model=SummarizeResponse)
def summarize_text(request: SummarizeRequest):
    result = summarize_text_by_filename(request.saved_filename)
    return result
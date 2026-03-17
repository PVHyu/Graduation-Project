from fastapi import APIRouter

from app.schemas.extract import ExtractRequest, ExtractResponse
from app.services.extract_service import extract_text_by_filename

router = APIRouter()


@router.post("/", response_model=ExtractResponse)
def extract_text(request: ExtractRequest):
    result = extract_text_by_filename(request.saved_filename)
    return result
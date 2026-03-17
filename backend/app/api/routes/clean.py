from fastapi import APIRouter

from app.schemas.clean import CleanRequest, CleanResponse
from app.services.clean_service import clean_text_by_filename

router = APIRouter()


@router.post("/", response_model=CleanResponse)
def clean_text(request: CleanRequest):
    result = clean_text_by_filename(request.saved_filename)
    return result
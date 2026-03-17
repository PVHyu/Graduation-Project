from fastapi import APIRouter

from app.schemas.mock import MockAnalyzeRequest, MockAnalyzeResponse
from app.services.mock_service import generate_mock_result

router = APIRouter()


@router.post("/analyze", response_model=MockAnalyzeResponse)
def mock_analyze(request: MockAnalyzeRequest):
    result = generate_mock_result(request.saved_filename)
    return result
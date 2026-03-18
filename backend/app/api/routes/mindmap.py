from fastapi import APIRouter

from app.schemas.mindmap import MindmapRequest, MindmapResponse
from app.services.mindmap_service import generate_mindmap_by_filename

router = APIRouter()


@router.post("/", response_model=MindmapResponse)
def generate_mindmap(request: MindmapRequest):
    result = generate_mindmap_by_filename(request.saved_filename)
    return result
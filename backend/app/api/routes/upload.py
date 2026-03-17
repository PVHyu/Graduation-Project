from fastapi import APIRouter, File, UploadFile

from app.schemas.response import UploadResponse
from app.services.file_service import save_uploaded_file

router = APIRouter()


@router.get("/test")
def test_upload_route():
    return {"message": "Upload route is ready"}


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    result = await save_uploaded_file(file)
    return result
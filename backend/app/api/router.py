from fastapi import APIRouter
from app.api.routes import (
    health,
    upload,
    extract,
    clean,
    mock,
    summarize,
    mindmap,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(extract.router, prefix="/extract", tags=["Extract"])
api_router.include_router(clean.router, prefix="/clean", tags=["Clean"])
api_router.include_router(mock.router, prefix="/mock", tags=["Mock"])
api_router.include_router(summarize.router, prefix="/summarize", tags=["Summarize"])
api_router.include_router(mindmap.router, prefix="/mindmap", tags=["Mindmap"])
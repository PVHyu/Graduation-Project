from __future__ import annotations

from pydantic import BaseModel, Field


class MindmapNode(BaseModel):
    title: str
    children: list["MindmapNode"] = Field(default_factory=list)


MindmapNode.model_rebuild()


class MockAnalyzeRequest(BaseModel):
    saved_filename: str


class MockAnalyzeResponse(BaseModel):
    saved_filename: str
    summary: str
    main_points: list[str]
    mindmap: MindmapNode
    clean_text_preview: str
    message: str
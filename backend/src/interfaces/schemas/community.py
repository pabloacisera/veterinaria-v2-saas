from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreatePostRequest(BaseModel):
    contenido: str
    imagen_url: Optional[str] = None


class PostResponse(BaseModel):
    id: UUID
    company_id: UUID
    contenido: str
    imagen_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PostDetailResponse(BaseModel):
    id: UUID
    company_id: UUID
    contenido: str
    imagen_url: Optional[str] = None
    created_at: datetime
    comments: list["CommentResponse"]
    likes_count: int

    model_config = {"from_attributes": True}


class CreateCommentRequest(BaseModel):
    contenido: str


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    company_id: UUID
    contenido: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LikeResponse(BaseModel):
    liked: bool
    count: int

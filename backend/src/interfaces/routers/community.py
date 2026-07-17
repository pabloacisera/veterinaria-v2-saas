from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.application.use_cases.community import (
    CreateCommentUseCase,
    CreatePostUseCase,
    DeletePostUseCase,
    GetPostDetailUseCase,
    ListPostsFeedUseCase,
    ToggleLikeUseCase,
)
from src.infrastructure.di import get_container
from src.interfaces.dependencies import get_company_id
from src.interfaces.schemas.community import (
    CommentResponse,
    CreateCommentRequest,
    CreatePostRequest,
    LikeResponse,
    PostDetailResponse,
    PostResponse,
)

router = APIRouter(prefix="/api/v1/comunidad", tags=["comunidad"])


@router.get("/posts", response_model=list[PostResponse])
async def list_posts_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    container=Depends(get_container),
):
    use_case = container.resolve(ListPostsFeedUseCase)
    return await use_case.execute(limit=limit, offset=offset)


@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    body: CreatePostRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreatePostUseCase)
    try:
        return await use_case.execute(
            company_id=company_id,
            contenido=body.contenido,
            imagen_url=body.imagen_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/posts/{post_id}", response_model=PostDetailResponse)
async def get_post_detail(
    post_id: UUID,
    container=Depends(get_container),
):
    use_case = container.resolve(GetPostDetailUseCase)
    try:
        post, comments, likes_count = await use_case.execute(post_id=post_id)
        return PostDetailResponse(
            id=post.id,
            company_id=post.company_id,
            contenido=post.contenido,
            imagen_url=post.imagen_url,
            created_at=post.created_at,
            comments=[CommentResponse.model_validate(c) for c in comments],
            likes_count=likes_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/posts/{post_id}/comentarios", response_model=CommentResponse, status_code=201)
async def add_comment(
    post_id: UUID,
    body: CreateCommentRequest,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(CreateCommentUseCase)
    try:
        return await use_case.execute(
            post_id=post_id,
            company_id=company_id,
            contenido=body.contenido,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/posts/{post_id}/like", response_model=LikeResponse)
async def toggle_like(
    post_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(ToggleLikeUseCase)
    try:
        liked, count = await use_case.execute(post_id=post_id, company_id=company_id)
        return LikeResponse(liked=liked, count=count)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: UUID,
    container=Depends(get_container),
    company_id: UUID = Depends(get_company_id),
):
    use_case = container.resolve(DeletePostUseCase)
    try:
        await use_case.execute(post_id=post_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

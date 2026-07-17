from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.community import Comment, Post


class CommunityRepository(ABC):
    @abstractmethod
    async def create_post(self, post: Post) -> Post: ...

    @abstractmethod
    async def get_post(self, post_id: UUID) -> Post | None: ...

    @abstractmethod
    async def list_posts(self, company_ids_to_exclude: list[UUID], limit: int, offset: int) -> list[Post]: ...

    @abstractmethod
    async def soft_delete_post(self, post_id: UUID, company_id: UUID) -> bool: ...

    @abstractmethod
    async def create_comment(self, comment: Comment) -> Comment: ...

    @abstractmethod
    async def list_comments(self, post_id: UUID) -> list[Comment]: ...

    @abstractmethod
    async def toggle_like(self, post_id: UUID, company_id: UUID) -> tuple[bool, int]: ...

    @abstractmethod
    async def count_likes(self, post_id: UUID) -> int: ...

    @abstractmethod
    async def count_comments(self, post_id: UUID) -> int: ...

from uuid import UUID

from src.domain.entities.community import Comment, Post


class CreatePostUseCase:
    def __init__(self, post_repo, company_repo):
        self.post_repo = post_repo
        self.company_repo = company_repo

    async def execute(self, company_id: UUID, contenido: str, imagen_url: str | None = None) -> Post:
        company = await self.company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Compañía no encontrada")
        if company.invisible:
            raise ValueError("Compañía invisible no puede crear posts")

        post = Post(company_id=company_id, contenido=contenido, imagen_url=imagen_url)
        return await self.post_repo.create_post(post)


class ListPostsFeedUseCase:
    def __init__(self, post_repo, company_repo):
        self.post_repo = post_repo
        self.company_repo = company_repo

    async def execute(self, limit: int = 20, offset: int = 0) -> list[Post]:
        invisible = await self.company_repo.list_invisible()
        exclude_ids = [c.id for c in invisible]
        return await self.post_repo.list_posts(exclude_ids, limit, offset)


class GetPostDetailUseCase:
    def __init__(self, post_repo):
        self.post_repo = post_repo

    async def execute(self, post_id: UUID) -> tuple[Post, list[Comment], int]:
        post = await self.post_repo.get_post(post_id)
        if not post:
            raise ValueError("Post no encontrado")

        comments = await self.post_repo.list_comments(post_id)
        likes_count = await self.post_repo.count_likes(post_id)
        return post, comments, likes_count


class CreateCommentUseCase:
    def __init__(self, post_repo, company_repo):
        self.post_repo = post_repo
        self.company_repo = company_repo

    async def execute(self, post_id: UUID, company_id: UUID, contenido: str) -> Comment:
        post = await self.post_repo.get_post(post_id)
        if not post:
            raise ValueError("Post no encontrado")

        company = await self.company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Compañía no encontrada")
        if company.invisible:
            raise ValueError("Compañía invisible no puede comentar")

        comment = Comment(post_id=post_id, company_id=company_id, contenido=contenido)
        return await self.post_repo.create_comment(comment)


class ToggleLikeUseCase:
    def __init__(self, post_repo, company_repo):
        self.post_repo = post_repo
        self.company_repo = company_repo

    async def execute(self, post_id: UUID, company_id: UUID) -> tuple[bool, int]:
        post = await self.post_repo.get_post(post_id)
        if not post:
            raise ValueError("Post no encontrado")

        company = await self.company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Compañía no encontrada")
        if company.invisible:
            raise ValueError("Compañía invisible no puede dar like")

        return await self.post_repo.toggle_like(post_id, company_id)


class DeletePostUseCase:
    def __init__(self, post_repo):
        self.post_repo = post_repo

    async def execute(self, post_id: UUID, company_id: UUID):
        post = await self.post_repo.get_post(post_id)
        if not post:
            raise ValueError("Post no encontrado")
        if post.company_id != company_id:
            raise ValueError("No puedes eliminar un post de otra compañía")

        deleted = await self.post_repo.soft_delete_post(post_id, company_id)
        if not deleted:
            raise ValueError("No se pudo eliminar el post")

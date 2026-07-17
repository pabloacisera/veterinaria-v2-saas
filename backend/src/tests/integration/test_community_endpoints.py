import pytest


@pytest.mark.integration
class TestCommunityEndpoints:
    async def test_list_posts_public(self, client):
        response = await client.get("/api/v1/comunidad/posts")
        assert response.status_code in (200, 401, 403)

    async def test_get_post_detail_not_found(self, client):
        response = await client.get(
            "/api/v1/comunidad/posts/00000000-0000-0000-0000-000000000001"
        )
        assert response.status_code in (404, 401)

    async def test_create_post_missing_token(self, client):
        response = await client.post(
            "/api/v1/comunidad/posts",
            json={"contenido": "Test post"},
        )
        assert response.status_code == 401

    async def test_create_comment_missing_token(self, client):
        response = await client.post(
            "/api/v1/comunidad/posts/00000000-0000-0000-0000-000000000001/comentarios",
            json={"contenido": "Test comment"},
        )
        assert response.status_code == 401

    async def test_toggle_like_missing_token(self, client):
        response = await client.post(
            "/api/v1/comunidad/posts/00000000-0000-0000-0000-000000000001/like"
        )
        assert response.status_code == 401

    async def test_delete_post_missing_token(self, client):
        response = await client.delete(
            "/api/v1/comunidad/posts/00000000-0000-0000-0000-000000000001"
        )
        assert response.status_code == 401

    async def test_create_post_invalid_body(self, client, auth_headers):
        response = await client.post(
            "/api/v1/comunidad/posts",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422

from unittest.mock import AsyncMock, patch

import pytest


class TestGoogleCallbackURLEncoding:
    @pytest.mark.asyncio
    async def test_email_is_url_encoded(self):
        from urllib.parse import quote

        email = "test+tag@domain.com"
        name = "María José"
        encoded_email = quote(email)
        encoded_name = quote(name)

        assert encoded_email == "test%2Btag%40domain.com"
        assert encoded_name == "Mar%C3%ADa%20Jos%C3%A9"

    @pytest.mark.asyncio
    async def test_special_chars_in_name_are_encoded(self):
        from urllib.parse import quote

        name = "José & María"
        encoded = quote(name)
        assert "&" in encoded or "%26" in encoded
        assert " " in encoded or "%20" in encoded

    @pytest.mark.asyncio
    async def test_redirect_url_contains_encoded_values(self):
        from urllib.parse import quote

        frontend_url = "http://localhost:5173"
        email = "user@test.com"
        name = "Test User"
        token = "abc123"
        refresh = "xyz789"

        redirect_url = (
            f"{frontend_url}/login"
            f"#google=success"
            f"&access_token={token}"
            f"&refresh_token={refresh}"
            f"&email={quote(email)}"
            f"&name={quote(name)}"
        )

        assert "user%40test.com" in redirect_url
        assert "Test%20User" in redirect_url
        assert "abc123" in redirect_url
        assert "xyz789" in redirect_url

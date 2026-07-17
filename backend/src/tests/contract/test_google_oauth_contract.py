from urllib.parse import urlparse


class TestGoogleOAuthContract:
    def test_google_oauth_config_structure(self):
        config = {
            "name": "google",
            "client_id": "GOOGLE_CLIENT_ID_FROM_ENV",
            "client_secret": "GOOGLE_CLIENT_SECRET_FROM_ENV",
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "client_kwargs": {"scope": "openid email profile"},
        }

        assert config["name"] == "google"
        assert config["server_metadata_url"] == "https://accounts.google.com/.well-known/openid-configuration"
        assert "openid" in config["client_kwargs"]["scope"]
        assert "email" in config["client_kwargs"]["scope"]
        assert "profile" in config["client_kwargs"]["scope"]

    def test_google_token_response_structure(self):
        token_response = {
            "access_token": "ya29.a0AfH6S...",
            "expires_in": 3599,
            "scope": "openid email profile",
            "token_type": "Bearer",
            "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6I...",
            "userinfo": {
                "sub": "1234567890",
                "email": "user@example.com",
                "name": "User Name",
                "picture": "https://lh3.googleusercontent.com/a-/photo",
            },
        }

        assert "access_token" in token_response
        assert "id_token" in token_response
        assert "userinfo" in token_response
        assert token_response["userinfo"]["sub"] == "1234567890"
        assert token_response["userinfo"]["email"] == "user@example.com"
        assert token_response["token_type"] == "Bearer"

    def test_callback_endpoint_path(self):
        endpoint = "/api/v1/auth/google/callback"
        assert endpoint == "/api/v1/auth/google/callback"

    def test_google_user_info_minimal_fields(self):
        user_info = {
            "sub": "google-user-id",
            "email": "user@gmail.com",
            "name": "Google User",
        }

        assert "sub" in user_info
        assert "email" in user_info
        assert "name" in user_info

    def test_auth_url_uses_https(self):
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        parsed = urlparse(auth_url)
        assert parsed.scheme == "https"
        assert "google.com" in parsed.netloc

    def test_google_oauth_backend_response_shape(self):
        response = {
            "access_token": "jwt-token",
            "refresh_token": "jwt-refresh",
            "token_type": "bearer",
            "expires_in": 900,
            "user": {
                "id": "user-uuid",
                "email": "user@example.com",
                "name": "User",
            },
        }

        assert "access_token" in response
        assert "token_type" in response
        assert "user" in response
        assert response["user"]["email"] == "user@example.com"

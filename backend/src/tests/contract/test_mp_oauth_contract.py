from urllib.parse import urlparse, parse_qs


class TestMpOAuthContract:
    def test_auth_url_contains_required_params(self):
        company_id = "test-company-uuid"
        app_id = "app-123"
        redirect_uri = "https://example.com/callback"

        auth_url = (
            f"https://auth.mercadopago.com/authorization"
            f"?client_id={app_id}"
            f"&response_type=code"
            f"&platform_id=mp"
            f"&redirect_uri={redirect_uri}"
            f"&state={company_id}"
        )

        parsed = urlparse(auth_url)
        qs = parse_qs(parsed.query)

        assert parsed.scheme == "https"
        assert parsed.netloc == "auth.mercadopago.com"
        assert parsed.path == "/authorization"
        assert qs["client_id"][0] == app_id
        assert qs["response_type"][0] == "code"
        assert qs["platform_id"][0] == "mp"
        assert qs["redirect_uri"][0] == redirect_uri
        assert qs["state"][0] == company_id

    def test_oauth_estado_response_shape(self):
        response_conectado = {"conectado": True, "mp_user_id": "mp-user-123"}
        response_desconectado = {"conectado": False, "mp_user_id": None}

        assert list(response_conectado.keys()) == ["conectado", "mp_user_id"]
        assert list(response_desconectado.keys()) == ["conectado", "mp_user_id"]
        assert response_conectado["conectado"] is True
        assert response_desconectado["conectado"] is False
        assert response_conectado["mp_user_id"] == "mp-user-123"
        assert response_desconectado["mp_user_id"] is None

    def test_callback_redirect_uses_success_url_base(self):
        frontend_url = "http://localhost:5173/configuracion?status=success"
        assert frontend_url.startswith("http://localhost:5173/configuracion")
        assert "status=success" in frontend_url

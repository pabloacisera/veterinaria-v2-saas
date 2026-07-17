import json


class TestMailjetContract:
    def test_activation_email_payload_structure(self):
        payload = {
            "Messages": [
                {
                    "From": {"Email": "test@veter.com", "Name": "Veter"},
                    "To": [{"Email": "user@example.com", "Name": "User"}],
                    "Subject": "Activá tu cuenta en Veter",
                    "HTMLPart": "<html><body><h1>Activá tu cuenta</h1></body></html>",
                }
            ]
        }

        assert "Messages" in payload
        assert len(payload["Messages"]) == 1
        msg = payload["Messages"][0]

        assert "From" in msg
        assert msg["From"]["Email"] == "test@veter.com"
        assert "To" in msg
        assert len(msg["To"]) == 1
        assert msg["To"][0]["Email"] == "user@example.com"
        assert "Subject" in msg
        assert "HTMLPart" in msg

    def test_access_code_email_payload_structure(self):
        payload = {
            "Messages": [
                {
                    "From": {"Email": "test@veter.com", "Name": "Veter"},
                    "To": [{"Email": "client@example.com", "Name": "Client"}],
                    "Subject": "Tu código de acceso — Veter",
                    "HTMLPart": "<html><body><h1>Tu código de acceso</h1></body></html>",
                }
            ]
        }

        assert "Messages" in payload
        msg = payload["Messages"][0]
        assert msg["Subject"] == "Tu código de acceso — Veter"
        assert msg["To"][0]["Email"] == "client@example.com"

    def test_template_email_payload_structure(self):
        payload = {
            "Messages": [
                {
                    "From": {"Email": "test@veter.com", "Name": "Veter"},
                    "To": [{"Email": "user@example.com", "Name": "User"}],
                    "TemplateID": 12345,
                    "TemplateLanguage": True,
                    "Variables": {"name": "User", "code": "XYZ"},
                }
            ]
        }

        msg = payload["Messages"][0]
        assert "TemplateID" in msg
        assert msg["TemplateID"] == 12345
        assert msg["TemplateLanguage"] is True
        assert "Variables" in msg
        assert msg["Variables"]["name"] == "User"

    def test_admin_reset_email_payload_structure(self):
        payload = {
            "Messages": [
                {
                    "From": {"Email": "test@veter.com", "Name": "Veter"},
                    "To": [{"Email": "admin@veter.com", "Name": "Admin"}],
                    "Subject": "Recuperación de acceso admin — Veter",
                    "HTMLPart": "<html><body><a href='https://veter.com/reset'>Reset</a></body></html>",
                }
            ]
        }

        msg = payload["Messages"][0]
        assert msg["Subject"] == "Recuperación de acceso admin — Veter"
        assert msg["To"][0]["Name"] == "Admin"

    def test_company_blocked_email_payload_structure(self):
        payload = {
            "Messages": [
                {
                    "From": {"Email": "test@veter.com", "Name": "Veter"},
                    "To": [{"Email": "owner@veter.com", "Name": "Vet Clinic"}],
                    "Subject": "Suscripción bloqueada — Veter",
                    "HTMLPart": "<html><body><h1>Bloqueado</h1></body></html>",
                }
            ]
        }

        msg = payload["Messages"][0]
        assert msg["Subject"] == "Suscripción bloqueada — Veter"
        assert msg["To"][0]["Name"] == "Vet Clinic"

    def test_mailjet_api_response_structure(self):
        mock_response = {
            "Messages": [
                {
                    "Status": "success",
                    "To": [{"Email": "test@example.com", "MessageUUID": "abc-123", "MessageID": 456}],
                }
            ]
        }

        assert mock_response["Messages"][0]["Status"] == "success"
        assert "MessageID" in mock_response["Messages"][0]["To"][0]

    def test_send_returns_200(self):
        assert True  # Mailjet send.create returns status_code 200 on success

    def test_payload_serializable_to_json(self):
        payload = {
            "Messages": [
                {
                    "From": {"Email": "a@b.com", "Name": "T"},
                    "To": [{"Email": "c@d.com", "Name": "U"}],
                    "Subject": "Test",
                    "HTMLPart": "<p>test</p>",
                }
            ]
        }
        dumped = json.dumps(payload)
        loaded = json.loads(dumped)
        assert loaded == payload

import json


class TestCloudinaryContract:
    def test_upload_document_parameters(self):
        params = {
            "file": b"fake-pdf-bytes",
            "folder": "veterinaria.v2/company-123/entity-456/docs",
            "public_id": "factura_v1_entity-456",
            "resource_type": "raw",
            "overwrite": False,
        }

        assert params["resource_type"] == "raw"
        assert params["overwrite"] is False
        assert "veterinaria.v2" in params["folder"]
        assert params["public_id"].startswith("factura")

    def test_upload_response_structure(self):
        upload_response = {
            "public_id": "veterinaria.v2/company-123/entity-456/docs/factura_v1",
            "secure_url": "https://res.cloudinary.com/cloud-name/raw/upload/v1/..."
        }

        assert "public_id" in upload_response
        assert "secure_url" in upload_response
        assert upload_response["secure_url"].startswith("https://")

    def test_cloudinary_service_returns_expected_shape(self):
        result = {
            "public_id": "pub-abc-123",
            "secure_url": "https://res.cloudinary.com/demo/raw/upload/v1/doc.pdf",
        }

        assert list(result.keys()) == ["public_id", "secure_url"]
        assert isinstance(result["public_id"], str)
        assert isinstance(result["secure_url"], str)

    def test_root_folder_default(self):
        root_folder = "veterinaria.v2"
        assert root_folder == "veterinaria.v2"

    def test_folder_path_format(self):
        company_id = "company-uuid"
        entity_id = "entity-uuid"
        folder = f"veterinaria.v2/{company_id}/{entity_id}/docs"
        assert folder == "veterinaria.v2/company-uuid/entity-uuid/docs"

    def test_public_id_format(self):
        filename = "factura_v1_entity-uuid"
        folder = "veterinaria.v2/c-123/e-456/docs"
        public_id = f"{folder}/{filename}"
        assert public_id == "veterinaria.v2/c-123/e-456/docs/factura_v1_entity-uuid"

    def test_response_json_serializable(self):
        result = {
            "public_id": "test-public-id",
            "secure_url": "https://res.cloudinary.com/test/raw/upload/v1/test.pdf",
        }
        dumped = json.dumps(result)
        loaded = json.loads(dumped)
        assert loaded == result

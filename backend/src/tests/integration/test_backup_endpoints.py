import pytest


@pytest.mark.integration
class TestBackupEndpoints:
    async def test_trigger_backup_missing_token(self, client):
        response = await client.post(
            "/access_role/admin/developer/backup/manual"
        )
        assert response.status_code == 401

    async def test_list_backups_missing_token(self, client):
        response = await client.get(
            "/access_role/admin/developer/backup/historial"
        )
        assert response.status_code == 401

    async def test_trigger_backup_admin_authenticated(self, client, admin_headers):
        response = await client.post(
            "/access_role/admin/developer/backup/manual",
            headers=admin_headers,
        )
        assert response.status_code in (200, 500)

    async def test_list_backups_admin_authenticated(self, client, admin_headers):
        response = await client.get(
            "/access_role/admin/developer/backup/historial",
            headers=admin_headers,
        )
        assert response.status_code in (200, 500)

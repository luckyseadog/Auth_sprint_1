import pytest
from httpx import codes

@pytest.mark.asyncio
async def test_assign_role(client):
    response = await client.post('/admin/user_role/assign')
    assert response.status_code == codes.UNAUTHORIZED


@pytest.mark.asyncio
async def test_revoke_role(client):
    response = await client.post('/admin/user_role/revoke')
    assert response.status_code == codes.UNAUTHORIZED


@pytest.mark.asyncio
async def test_check_role(client):
    response = await client.post('/admin/user_role/check')
    assert response.status_code == codes.UNAUTHORIZED

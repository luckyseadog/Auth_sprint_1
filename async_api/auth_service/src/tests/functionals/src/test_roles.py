import pytest
from uuid import uuid4
from fastapi import status
ID_ROLE = str(uuid4())

test_role_create = {
    'id': ID_ROLE,
    'title': 'test role',
    'description': 'test role description',
}

test_role_update_or_delete = {
    'id': '28813998-4098-4c8d-b4f0-08c1169390c1',
    'title': 'user',
    'description': 'user role',
}

@pytest.mark.asyncio
async def test_get_roles(client, superadmin_cookies, roles_in_db):
    response = await client.get(
        '/admin/roles',
        cookies=superadmin_cookies,
    )
    roles = response.json()
    list_roles = [item['title'] for item in roles]
    assert len(roles) == 5
    assert 'superadmin' in list_roles
    assert 'admin' in list_roles
    assert 'user' in list_roles
    assert 'guest' in list_roles
    assert 'subscriber' in list_roles
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_create_role(client, superadmin_cookies):
    response = await client.post(
        url='/admin/roles',
        json=test_role_create,
        cookies=superadmin_cookies,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_role_create
    response = await client.get('/admin/roles', cookies=superadmin_cookies)
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_existing_role(client, superadmin_cookies, roles_in_db):
    test_role_update_or_delete['title'] = 'new_user_role'
    response = await client.put(
        url='/admin/roles',
        json=test_role_update_or_delete,
        cookies=superadmin_cookies,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_role_update_or_delete


@pytest.mark.asyncio
async def test_update_not_existing_role(client, superadmin_cookies):
    response = await client.put(
        url='/admin/roles',
        json=test_role_update_or_delete,
        cookies=superadmin_cookies,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': f'role with id {test_role_update_or_delete["id"]} does not exist'}


@pytest.mark.asyncio
async def test_delete_existing_role(client, superadmin_cookies, roles_in_db):
    response = await client.delete(
        url='/admin/roles',
        cookies=superadmin_cookies,
        params={'role_id': test_role_update_or_delete['id']},
    )
    assert response.json() is not None
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_not_existing_role(client, superadmin_cookies):
    response = await client.delete(
        url='/admin/roles',
        cookies=superadmin_cookies,
        params={'role_id': test_role_update_or_delete['id']},
    )
    assert response.json() is None
    assert response.status_code == status.HTTP_200_OK

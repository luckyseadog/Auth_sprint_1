import pytest
from httpx import codes
from faker import Faker
from tests.settings import settings

faker = Faker()

my_test_user = {
    'login': faker.user_name(),
    'password': faker.password(),
    'first_name': faker.first_name(),
    'last_name': faker.last_name(),
    'email': faker.email(),
}

user_for_update_or_delete = {
    'id': 'd7450665-ae1f-4497-ba7d-6f8f5e403c7a',
    'login': 'uvillanueva',
    'email': 'johnsonjoshua@example.org',
    'password': '!dPx98Kp&o',
    'first_name': 'Rebecca',
    'last_name': 'Miller',
}


@pytest.mark.asyncio
async def test_get_users(client, superadmin_cookies, users_in_db):
    response = await client.get(
        url='/users',
        cookies=superadmin_cookies,
    )
    assert response.status_code == codes.OK
    assert len(response.json()) == 11


@pytest.mark.asyncio
async def test_create_user(client, superadmin_cookies):
    response = await client.post(
        url='/signup',
        headers={'Origin': settings.root_path},
        cookies=superadmin_cookies,
        json=my_test_user,
    )

    assert response.status_code == codes.OK
    assert response.json()['login'] == my_test_user['login']
    assert response.json()['email'] == my_test_user['email']
    assert response.json()['first_name'] == my_test_user['first_name']
    assert response.json()['last_name'] == my_test_user['last_name']


@pytest.mark.asyncio
async def test_update_existing_user(client, superadmin_cookies, users_in_db):
    user_for_update_or_delete['login'] = 'updated_login'
    user_for_update_or_delete['email'] = 'updated_email@example.org'

    response = await client.put(
        url='/users',
        headers={'Origin': settings.root_path},
        cookies=superadmin_cookies,
        json=user_for_update_or_delete,
    )

    assert response.status_code == codes.OK
    assert response.json()['login'] == 'updated_login'
    assert response.json()['email'] == 'updated_email@example.org'


@pytest.mark.asyncio
async def test_update_not_existing_user(client, superadmin_cookies):

    response = await client.put(
        url='/users',
        headers={'Origin': settings.root_path},
        cookies=superadmin_cookies,
        json=user_for_update_or_delete,
    )

    assert response.status_code == codes.NOT_FOUND
    assert response.json() == {'detail': f'User with id {user_for_update_or_delete["id"]} not found'}


@pytest.mark.asyncio
async def test_delete_existing_user(client, superadmin_cookies, users_in_db):

    response = await client.delete(
        url='/users',
        headers={'Origin': settings.root_path},
        cookies=superadmin_cookies,
        params={'user_id': user_for_update_or_delete['id']},
    )
    print(response.json())
    assert response.status_code == codes.OK
    assert response.json()['deleted_at'] != ''


@pytest.mark.asyncio
async def test_delete_not_existing_user(client, superadmin_cookies):

    response = await client.delete(
        url='/users',
        headers={'Origin': settings.root_path},
        cookies=superadmin_cookies,
        params={'user_id': user_for_update_or_delete['id']},
    )

    print(response.json())
    assert response.status_code == codes.NOT_FOUND
    assert response.json() == {'detail': f'User with id {user_for_update_or_delete["id"]} not found'}


@pytest.mark.asyncio
async def test_get_me(client, superadmin_cookies):
    response = await client.get(
        url='/users/me',
        cookies=superadmin_cookies,
    )
    print(response.json())
    assert response.status_code == codes.OK
    assert response.json()['login'] == settings.sa_login
    assert response.json()['email'] == settings.sa_email


# @pytest.mark.asyncio
# async def test_login(client, prepare_database):
#     response = await client.post(
#         '/login',
#         headers={'Origin': settings.root_path},
#         data={
#             'username': my_test_user['login'],
#             'password': my_test_user['password'],
#         },
#     )
#     assert response.status_code == codes.OK
#
# @pytest.mark.asyncio
# async def test_logout(client):
#     response = await client.post('/logout')
#     assert response.status_code == 401

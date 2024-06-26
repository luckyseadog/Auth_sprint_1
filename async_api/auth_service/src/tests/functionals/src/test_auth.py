import pytest
from tests.settings import settings
from fastapi import status


test_superadmin = {
    'login': settings.sa_login,
    'password': settings.sa_password,
    'email': settings.sa_email,
    'first_name': settings.sa_firstname,
    'last_name': settings.sa_lastname,
}

test_user = {
    'login': 'login',
    'password': 'password',
    'email': 'login@email.com',
    'first_name': 'first_name',
    'last_name': 'last_name',
}


@pytest.mark.asyncio
async def test_signup(client, superadmin_cookies):

    response = await client.post(
        url='/signup',
        json=test_user,
        headers={'Origin': settings.root_path},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['login'] == test_user['login']
    assert response.json()['email'] == test_user['email']


@pytest.mark.asyncio
async def test_success_login(client, superadmin_cookies):

    response = await client.post(
        url='/login',
        data={
            'username': settings.sa_login,
            'password': settings.sa_password,
        },
        headers={'Origin': settings.root_path},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get('access_token') is not None
    assert response.cookies.get('refresh_token') is not None

@pytest.mark.asyncio
async def test_unsuccess_login(client, superadmin_cookies):

    response = await client.post(
        url='/login',
        data={
            'username': 'username',
            'password': 'password',
        },
        headers={'Origin': settings.root_path},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.cookies.get('access_token') is None
    assert response.cookies.get('refresh_token') is None


@pytest.mark.asyncio
async def test_logout(client, superadmin_cookies):

    response = await client.post(
        url='/logout',
        cookies=superadmin_cookies,
        headers={'Origin': settings.root_path},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get('access_token') is None
    assert response.cookies.get('refresh_token') is None


@pytest.mark.asyncio
async def test_refresh(client, superadmin_cookies):

    response = await client.post(
        url='/refresh',
        cookies=superadmin_cookies,
        headers={'Origin': settings.root_path},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get('access_token') is not None
    assert response.cookies.get('refresh_token') is not None


@pytest.mark.asyncio
async def test_refresh_invalid_token(client, superadmin_cookies):

    superadmin_cookies['refresh_token'] += '1'

    response = await client.post(
        url='/refresh',
        cookies=superadmin_cookies,
        headers={'Origin': settings.root_path},
    )

    print(response.json())
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Invalid refresh token'}

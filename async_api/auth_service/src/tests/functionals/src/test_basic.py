import pytest
from httpx import codes


@pytest.mark.parametrize(
    'params, answer',
    [
        (
            {
                'url': '/admin/roles',
                'method': 'GET',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/admin/roles',
                'method': 'PUT',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/admin/roles',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/admin/roles',
                'method': 'DELETE',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/users',
                'method': 'GET',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/users',
                'method': 'PUT',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/users',
                'method': 'DELETE',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/users/me',
                'method': 'GET',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/users/history',
                'method': 'GET',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/admin/user_role/assign',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/admin/user_role/revoke',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/admin/user_role/check',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/logout',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/logout_all',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/refresh',
                'method': 'POST',
            },
            {'status': codes.UNAUTHORIZED},
        ),
        (
            {
                'url': '/signup',
                'method': 'POST',
            },
            {'status': codes.BAD_REQUEST},
        ),
        (
            {
                'url': '/login',
                'method': 'POST',
            },
            {'status': codes.BAD_REQUEST},
        ),
    ],
    ids=[
        'GET /roles',
        'POST /roles',
        'PUT /roles',
        'DELETE /roles',
        'GET /users',
        'PUT /users',
        'DELETE /users',
        'GET /users/me',
        'GET /users/history',
        'POST /admin/user_role/assign',
        'POST /admin/user_role/revoke',
        'POST /admin/user_role/check',
        'POST /logout',
        'POST /logout_all',
        'POST /refresh',
        'POST /signup',
        'POST /login',
    ],
)
@pytest.mark.asyncio
async def test_protected_handlers(params, answer, client, prepare_database):
    data = {
        'GET': client.get,
        'POST': client.post,
        'PUT': client.put,
        'DELETE': client.delete,
    }
    response = await data[params['method']](params['url'])
    assert response.status_code == answer['status']

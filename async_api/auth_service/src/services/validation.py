import json
import time
from typing import Annotated, Union

from fastapi import Cookie, Header, Depends, HTTPException, status
from db.redis_db import Redis, get_redis
from core.config import settings
from schemas.entity_schemas import AccessTokenData, RefreshTokenData
from services.token_service import (
    AccessTokenService,
    get_access_token_service,
)


async def validate_access_token(
        user_agent: Annotated[Union[str, None], Header()] = None,
        access_token: Annotated[Union[str, None], Cookie()] = None,
        access_token_service: AccessTokenService = Depends(get_access_token_service),
        cache: Redis = Depends(get_redis),
) -> AccessTokenData:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access token',
        )

    if not access_token_service.validate_token(access_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid access token',
        )

    payload_str = access_token_service.decode_b64(access_token.split('.')[1])
    payload = json.loads(payload_str)

    # if await cache.check_banned_atoken(payload['sub'], access_token):
    user_id = payload['sub']
    if await cache.exists(f'{user_id}:login:{user_agent}:bannsed'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token is banned',
        )

    if payload['exp'] < time.time():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token is expired',
        )

    # if payload['iat'] < await cache.get_user_last_logout_all(payload['sub']):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail='Access token is withdrawn',
    #     )
    return AccessTokenData(**payload)


# async def get_current_user(
#         payload: Annotated[AccessTokenData, Depends(validate_access_token)],
#         user_service: Annotated[UserService, Depends(get_user_service)],
# ) -> User:
#     user = await user_service.get_user(payload.sub)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='user not found',
#         )
#     return user


# async def get_current_active_user(
#     user: Annotated[User, Depends(get_current_user)],
#     user_service: Annotated[UserService, Depends(get_user_service)],
# ) -> User:
#     if await user_service.is_deleted(user.id):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='User was deleted',
#         )
#     return user


# async def check_admin_or_super_admin_role(
#     user: Annotated[User, Depends(validate_access_token)],
# ) -> User:
#     roles = [role.title for role in user.roles]
#     if not (settings.role_admin in roles or settings.role_super_admin in roles):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
#     return user


async def check_admin_or_super_admin_role_from_access_token(
    payload: Annotated[AccessTokenData, Depends(validate_access_token)] = None,
) -> list[str]:
    if not (settings.role_admin in payload.roles or settings.role_super_admin in payload.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return payload


async def validate_refresh_token(
        user_agent: Annotated[Union[str, None], Header()] = None,
        refresh_token: Annotated[Union[str, None], Cookie()] = None,
        refresh_token_service: AccessTokenService = Depends(get_access_token_service),
        cache: Redis = Depends(get_redis),
) -> RefreshTokenData:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No refresh token',
        )

    if not refresh_token_service.validate_token(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid refresh token',
        )

    payload_str = refresh_token_service.decode_b64(refresh_token.split('.')[1])
    payload = json.loads(payload_str)

    # if await cache.check_valid_rtoken(payload['sub'], refresh_token) is False:
    user_id = payload['sub']
    if await cache.exists(f'{user_id}:login:{user_agent}:banned'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=' Refresh token is not valid',
        )

    # if payload['exp'] < time.time():
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail='Refresh token is expired',
    #     )

    return RefreshTokenData(**payload)


async def check_origin(origin: Annotated[str | None, Header()] = None):
    if origin is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Origin header is required',
        )
    return origin

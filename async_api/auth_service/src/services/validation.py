import json
from typing import Annotated, Union

from core.config import settings
from db.redis_db import RedisTokenStorage, get_redis
from fastapi import Cookie, Depends, Header, HTTPException, status
from schemas.entity_schemas import AccessTokenData, RefreshTokenData
from services.token_service import (AccessTokenService,
                                    get_access_token_service,
                                    get_refresh_token_service)


async def validate_access_token(
        user_agent: Annotated[Union[str, None], Header()] = None,
        access_token: Annotated[Union[str, None], Cookie()] = None,
        access_token_service: AccessTokenService = Depends(get_access_token_service),
        redis: RedisTokenStorage = Depends(get_redis),
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
    user_id = payload['sub']

    if await redis.check_banned_atoken(user_id, user_agent, access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token is banned',
        )

    # if payload['exp'] < time.time():
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail='Access token is expired',
    #     )

    if payload['iat'] < await redis.get_user_last_logout_all(user_id, user_agent):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token is withdrawn',
        )

    return AccessTokenData(**payload)


async def check_admin_or_super_admin_role_from_access_token(
        payload: Annotated[AccessTokenData, Depends(validate_access_token)] = None,
) -> list[str]:
    if not (settings.role_admin in payload.roles or settings.role_super_admin in payload.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return payload


async def validate_refresh_token(
        user_agent: Annotated[Union[str, None], Header()] = None,
        refresh_token: Annotated[Union[str, None], Cookie()] = None,
        refresh_token_service: AccessTokenService = Depends(get_refresh_token_service),
        redis: RedisTokenStorage = Depends(get_redis),
):
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
    user_id = payload['sub']

    if await redis.check_valid_rtoken(user_id, user_agent, refresh_token) is False:
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

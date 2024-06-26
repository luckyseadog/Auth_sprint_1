from datetime import datetime
from functools import lru_cache

from core.config import settings
from db.postgres_db import get_session
from db.redis_db import RedisTokenStorage, get_redis
from fastapi import Depends, HTTPException, status
from schemas.entity_schemas import TokenPairExpired, UserCredentials
from services.password_service import password_service
from services.token_service import AccessTokenService, RefreshTokenService
from services.user_service import UserService, get_user_service
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(
            self,
            db: AsyncSession,
            redis: RedisTokenStorage,
            user_service: UserService,
    ):
        self.db = db
        self.cache = redis
        self.user_service = user_service

    async def login(self, user_creds: UserCredentials, origin, user_agent) -> TokenPairExpired:
        user = await self.user_service.get_user_by_login(user_creds.login)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username or password',
            )

        password = user_creds.password
        target_password = user.password

        if not password_service.check_password(password, target_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Invalid username or password {password} {target_password}',
            )

        at = AccessTokenService()
        rt = RefreshTokenService()
        roles = [role.title for role in user.roles]
        access_token, access_exp = at.generate_token(origin, user.id, roles)
        refresh_token, refresh_exp = rt.generate_token(origin, user.id)

        # await self.cache.setex(
        #     f'{user.id}:login:{user_agent}',
        #     settings.refresh_token_weeks * 60 * 60 * 24 * 7,
        #     refresh_token,
        # )
        await self.cache.add_valid_rtoken(user.id, refresh_token, user_agent)
        return TokenPairExpired(
            access_token=access_token,
            refresh_token=refresh_token,
            access_exp=access_exp,
            refresh_exp=refresh_exp,
        )

    async def logout(self, user_id, access_token, refresh_token, user_agent):
        # await self.cache.delete_refresh(f'{user_id}:login:{user_agent}')
        # await self.cache.setex(
        #     f'{user_id}:logout:{user_agent}',
        #     settings.access_token_min * 60,
        #     access_token,
        # )
        await self.cache.delete_refresh(user_id, refresh_token, user_agent)
        await self.cache.add_banned_atoken(user_id, user_agent, access_token)
        return {'message': 'User logged out successfully'}

    async def logout_all(self, user_id, user_agent):
        # await self.cache.setex(
        #     f'{user_id}:logout:_all_',
        #     settings.access_token_min * 60,
        #     datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        # )
        # keys = await self.cache.keys(pattern=f'{user_id}:login:*')
        # await self.cache.delete(*keys)
        await self.cache.set_user_last_logout_all(user_id, user_agent)
        await self.cache.delete_refresh_all(user_id, user_agent)


    async def refresh(self, user_id, origin, user_agent):
        user = await self.user_service.get_user(user_id)
        at = AccessTokenService()
        rt = RefreshTokenService()
        roles = [role.title for role in user.roles]
        access_token, access_exp = at.generate_token(origin, user.id, roles)
        refresh_token, refresh_exp = rt.generate_token(origin, user.id)
        # await self.cache.setex(
        #     f'{user.id}:login:{user_agent}',
        #     settings.refresh_token_weeks * 60 * 60 * 24 * 7,
        #     refresh_token,
        # )
        await self.cache.add_valid_rtoken(user_id, refresh_token, user_agent)
        return TokenPairExpired(
            access_token=access_token,
            refresh_token=refresh_token,
            access_exp=access_exp,
            refresh_exp=refresh_exp,
        )


@lru_cache
def get_auth_service(
        db: AsyncSession = Depends(get_session),
        cache: RedisTokenStorage = Depends(get_redis),
        user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(
        db=db,
        redis=cache,
        user_service=user_service,
    )

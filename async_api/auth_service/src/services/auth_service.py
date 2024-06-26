from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings

from schemas.entity_schemas import UserCredentials
from services.password_service import password_service
from db.redis_db import Redis, get_redis
from db.postgres_db import get_session
from services.user_service import UserService, get_user_service
from schemas.entity_schemas import TokenPairExpired
from fastapi import HTTPException
from fastapi import status
from schemas.entity import History
from services.token_service import (
    AccessTokenService,
    RefreshTokenService,
)
from services.history_service import HistoryService, get_history_service
from datetime import datetime


class AuthService:
    def __init__(
            self,
            db: AsyncSession,
            redis: Redis,
            user_service: UserService,
            history_service: HistoryService,
    ):
        self.db = db
        self.cache = redis
        self.user_service = user_service
        self.history_service = history_service

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

        note = History(
            user_id=user.id,
            action='/login',
            fingerprint=user_agent,
        )
        await self.history_service.make_note(note)
        await self.cache.setex(
            f'{user.id}:login:{user_agent}',
            settings.refresh_token_weeks * 60 * 60 * 24 * 7,
            refresh_token,
        )
        return TokenPairExpired(
            access_token=access_token,
            refresh_token=refresh_token,
            access_exp=access_exp,
            refresh_exp=refresh_exp,
        )

    async def logout(self, user_id, access_token, user_agent):
        note = History(
            user_id=user_id,
            action='/logout',
            fingerprint=user_agent,
        )
        await self.history_service.make_note(note)

        await self.cache.delete(f'{user_id}:login:{user_agent}')
        await self.cache.setex(
            f'{user_id}:logout:{user_agent}',
            settings.access_token_min * 60,
            access_token,
        )
        return {'message': 'User logged out successfully'}

    async def logout_all(self, user_id, user_agent):
        note = History(
            user_id=user_id,
            action='/logout_all',
            fingerprint=user_agent,
        )
        await self.history_service.make_note(note)
        await self.cache.setex(
            f'{user_id}:logout:_all_',
            settings.access_token_min * 60,
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        )
        keys = await self.cache.keys(pattern=f'{user_id}:login:*')
        await self.cache.delete(*keys)

    async def refresh(self, user_id, origin, user_agent):
        user = await self.user_service.get_user(user_id)
        at = AccessTokenService()
        rt = RefreshTokenService()
        roles = [role.title for role in user.roles]
        access_token, access_exp = at.generate_token(origin, user.id, roles)
        refresh_token, refresh_exp = rt.generate_token(origin, user.id)
        await self.cache.setex(
            f'{user.id}:login:{user_agent}',
            settings.refresh_token_weeks * 60 * 60 * 24 * 7,
            refresh_token,
        )
        return TokenPairExpired(
            access_token=access_token,
            refresh_token=refresh_token,
            access_exp=access_exp,
            refresh_exp=refresh_exp,
        )


@lru_cache
def get_auth_service(
        db: AsyncSession = Depends(get_session),
        cache: Redis = Depends(get_redis),
        user_service: UserService = Depends(get_user_service),
        history_service: HistoryService = Depends(get_history_service),
) -> AuthService:
    return AuthService(
        db=db,
        redis=cache,
        user_service=user_service,
        history_service=history_service,
    )

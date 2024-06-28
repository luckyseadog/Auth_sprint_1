from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres_db import get_session
from sqlalchemy import select
from models.entity import UserModel, RoleModel
from services.exceptions import (
    role_already_exists,
    role_not_exists,
    user_not_found,
    role_not_found,
)


class AdminService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_user_role(self, user_id: str, role_id: str):
        query_user = select(UserModel).where(UserModel.id == user_id)
        query_role = select(RoleModel).where(RoleModel.id == role_id)

        res_user = await self.db.execute(query_user)
        res_role = await self.db.execute(query_role)
        user = res_user.scalars().one_or_none()
        role = res_role.scalars().one_or_none()

        if not role:
            raise role_not_found(role_id)
        if not user:
            raise user_not_found(user_id)
        if role in user.roles:
            raise role_already_exists(role_id)

        user.roles.append(role)
        await self.db.commit()
        return user

    async def revoke_user_role(self, user_id: str, role_id: str):
        query_user = select(UserModel).where(UserModel.id == user_id)
        query_role = select(RoleModel).where(RoleModel.id == role_id)

        res_user = await self.db.execute(query_user)
        res_role = await self.db.execute(query_role)
        user = res_user.scalars().one_or_none()
        role = res_role.scalars().one_or_none()

        if not role:
            raise role_not_found(role_id)
        if not user:
            raise user_not_found(user_id)
        if role not in user.roles:
            raise role_not_exists(role_id)

        user.roles.remove(role)
        await self.db.commit()
        return user

    async def check_user_role(self, user_id: str, role_id: str):
        query_user = select(UserModel).where(UserModel.id == user_id)
        query_role = select(RoleModel).where(RoleModel.id == role_id)

        res_user = await self.db.execute(query_user)
        res_role = await self.db.execute(query_role)
        user = res_user.scalars().one_or_none()
        role = res_role.scalars().one_or_none()

        if not role:
            raise role_not_found(role_id)
        if not user:
            raise user_not_found(user_id)

        return role in user.roles


@lru_cache
def get_admin_service(
        db: AsyncSession = Depends(get_session),
) -> AdminService:
    return AdminService(db=db)

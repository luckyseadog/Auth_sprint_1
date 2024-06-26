from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres_db import get_session
from sqlalchemy import select
from models.entity import UserModel, RoleModel
from schemas.entity import User, Role
from fastapi import HTTPException, status

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found role: {role_id}',
            )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found user: {user_id}',
            )

        if role in user.roles:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='role already exists',
            )

        user.roles.append(role)
        await self.db.commit()
        return User(
            id=user.id,
            login=user.login,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_superadmin=user.is_superadmin,
            roles=[
                Role(
                    id=role.id,
                    title=role.title,
                    description=role.description,
                ) for role in user.roles
            ],
        )

    async def revoke_user_role(self, user_id: str, role_id: str):
        query_user = select(UserModel).where(UserModel.id == user_id)
        query_role = select(RoleModel).where(RoleModel.id == role_id)

        res_user = await self.db.execute(query_user)
        res_role = await self.db.execute(query_role)
        user = res_user.scalars().one_or_none()
        role = res_role.scalars().one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found role: {role_id }',
            )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found user: {user_id}',
            )

        if role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'role {role_id} not fount in user',
            )

        user.roles.remove(role)
        await self.db.commit()
        return User(
            id=user.id,
            login=user.login,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_superadmin=user.is_superadmin,
            roles=[
                Role(
                    id=role.id,
                    title=role.title,
                    description=role.description,
                ) for role in user.roles
            ],
        )

    async def check_user_role(self, user_id: str, role_id: str):
        query_user = select(UserModel).where(UserModel.id == user_id)
        query_role = select(RoleModel).where(RoleModel.id == role_id)

        res_user = await self.db.execute(query_user)
        res_role = await self.db.execute(query_role)
        user = res_user.scalars().one_or_none()
        role = res_role.scalars().one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found role: {role_id}',
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found user: {user_id}',
            )

        return role in user.roles
        # if role not in user.roles:
        # raise HTTPException(
        #     status_code=status.HTTP_409_CONFLICT,
        #     detail='role not fount in user'
        # )


@lru_cache
def get_admin_service(
        db: AsyncSession = Depends(get_session),
) -> AdminService:
    return AdminService(db=db)

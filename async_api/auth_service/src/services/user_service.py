from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import RoleModel, UserModel
from schemas.entity import Role, User
from services.password_service import password_service
from functools import lru_cache
from db.postgres_db import get_session
from fastapi import Depends
from services.exceptions import (
    user_not_found,
    email_already_exists,
    login_already_exists,
    user_already_deleted,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> User:
        stmt = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
        user = stmt.scalars().one_or_none()
        if not user:
            raise user_not_found(user_id)
        return user

    async def get_user_by_email(self, user_email: str) -> User | None:
        stmt = await self.db.execute(select(UserModel).where(UserModel.email == user_email))
        user = stmt.scalars().one_or_none()
        if user:
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

    async def get_user_by_login(self, user_login) -> User:
        stmt = await self.db.execute(select(UserModel).where(UserModel.login == user_login))
        user = stmt.scalars().one_or_none()
        if user:
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

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(select(UserModel).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_user(self, user_create: User) -> User:
        user = await self.get_user_by_email(user_create.email)
        if user:
            raise email_already_exists(user_create.email)

        user = await self.get_user_by_login(user_create.login)
        if user:
            raise login_already_exists(user_create.login)

        user_create.password = password_service.compute_hash(user_create.password)
        user_dto = jsonable_encoder(user_create, exclude_none=True)

        if 'roles' in user_dto:
            new_roles = []
            for role in user_dto['roles']:
                result = await self.db.execute(select(RoleModel).where(RoleModel.title == role['title']))
                returned_role = result.scalars().one_or_none()
                if returned_role is None:
                    raise Exception
                new_roles.append(returned_role)

            user_dto['roles'] = new_roles

        user = UserModel(**user_dto)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user_create

    async def update_user(self, user_patch: User):
        user_patch.password = password_service.compute_hash(user_patch.password)

        user = await self.get_user_by_email(user_patch.email)
        if user and user.id != user_patch.id:
            raise email_already_exists(user_patch.email)
        user = await self.get_user_by_login(user_patch.login)
        if user and user.id != user_patch.id:
            raise login_already_exists(user_patch.login)

        query = (
            update(UserModel)
            .where(UserModel.id == user_patch.id)
            # .values(**user_patch.model_dump(exclude_none=True))
            .values({
                UserModel.login: user_patch.login,
                UserModel.password: user_patch.password,
                UserModel.first_name: user_patch.first_name,
                UserModel.last_name: user_patch.last_name,
                UserModel.email: user_patch.email,
            })
            .returning(UserModel)
        )
        result = await self.db.execute(query)
        updated_user = result.scalars().one_or_none()
        await self.db.commit()

        if not updated_user:
            raise user_not_found(user_patch.id)

        return updated_user

        # return User(
        #     id=updated_user.id,
        #     login=updated_user.login,
        #     password=updated_user.password,
        #     first_name=updated_user.first_name,
        #     last_name=updated_user.last_name,
        #     email=updated_user.email,
        #     is_superadmin=updated_user.is_superadmin,
        #     roles=[
        #         Role(
        #             id=role.id,
        #             title=role.title,
        #             description=role.description,
        #         ) for role in updated_user.roles
        #     ],
        # )

    async def delete_user(self, user_id: str) -> User:
        if not self.is_deleted(user_id):
            raise user_already_deleted(user_id)

        query = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(deleted_at=datetime.utcnow())
            .returning(UserModel)
        )

        result = await self.db.execute(query)
        deleted_user = result.scalars().one_or_none()
        await self.db.commit()
        if not deleted_user:
            raise user_not_found(user_id)
        return deleted_user

    async def is_deleted(self, user_id: str):
        user = await self.get_user(user_id)
        if not user:
            raise user_not_found(user_id)
        return False if user.deleted_at is None else True


@lru_cache
def get_user_service(
        db: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(db)

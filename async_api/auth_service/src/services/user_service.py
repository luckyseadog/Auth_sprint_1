from datetime import datetime
from functools import lru_cache

from db.postgres_db import get_session
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models.entity import RoleModel, UserModel
from schemas.entity import Role, User
from services.password_service import password_service
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> User:
        stmt = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
        user = stmt.scalars().one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'not found user: {user_id}',
            )
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
        return [
            User(
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
            ) for user in result.scalars()
        ]

    async def create_user(self, user_create: User) -> User:
        user = await self.get_user_by_email(user_create.email)
        if user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email already exists')

        user = await self.get_user_by_login(user_create.login)
        if user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='login already exists')

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
        return User(
            id=user.id,
            login=user.login,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_superadmin=user.is_superadmin,
            roles=[
                # jsonable_encoder(
                Role(
                    id=role.id,
                    title=role.title,
                    description=role.description,
                ) for role in user.roles
                #        )
            ],
        )

    async def update_user(self, user_patch: User):
        user_patch.password = password_service.compute_hash(user_patch.password)

        user = await self.get_user_by_email(user_patch.email)
        if user and user.id != user_patch.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'User with this email {user.email} already exists',
            )
        user = await self.get_user_by_login(user_patch.login)
        if user and user.id != user_patch.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'User with this login {user.login} already exists',
            )

        query = (
            update(UserModel)
            .where(UserModel.id == user_patch.id)
            .values(**user_patch.model_dump(exclude_none=True))
            .returning(UserModel)
        )
        result = await self.db.execute(query)
        updated_user = result.scalars().one_or_none()
        await self.db.commit()

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with id {user_patch.id} not found',
            )

        return User(
            id=updated_user.id,
            login=updated_user.login,
            password=updated_user.password,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email=updated_user.email,
            is_superadmin=updated_user.is_superadmin,
            roles=[
                Role(
                    id=role.id,
                    title=role.title,
                    description=role.description,
                ) for role in updated_user.roles
            ],
        )

    async def delete_user(self, user_id: str) -> User:

        if not self.is_deleted(user_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'User with id {user_id} already deleted',
            )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with id {user_id} not found',
            )
        return User(
            id=deleted_user.id,
            login=deleted_user.login,
            password=deleted_user.password,
            first_name=deleted_user.first_name,
            last_name=deleted_user.last_name,
            email=deleted_user.email,
            is_superadmin=deleted_user.is_superadmin,
            roles=[
                Role(
                    id=role.id,
                    title=role.title,
                    description=role.description,
                ) for role in deleted_user.roles
            ],
        )

    async def is_deleted(self, user_id: str):
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with id {user_id} not found',
            )
        return False if user.deleted_at is None else True


@lru_cache
def get_user_service(
        db: AsyncSession = Depends(get_session),
) -> UserService:
    # redis: RedisTokenStorage = Depends(get_redis)) -> UserService:
    return UserService(db)

import logging
from functools import lru_cache

from db.postgres_db import AsyncSession, get_session
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models.entity import RoleModel
from schemas.entity import Role
from sqlalchemy import delete, select, update


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role_create: Role) -> Role:
        role_dto = jsonable_encoder(role_create, exclude_none=True)
        role = RoleModel(**role_dto)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_roles(self, skip: int = 0, limit: int = 10) -> list[Role]:
        result = await self.db.execute(select(RoleModel).offset(skip).limit(limit))
        return [
            Role(
                id=role.id,
                title=role.title,
                description=role.description,
            ) for role in result.scalars()
        ]

    async def get_role_by_id(self, role_id: str) -> Role:
        result = await self.db.execute(select(RoleModel).where(RoleModel.id == role_id))
        returned_role = result.scalars().one_or_none()
        return Role(
            id=returned_role.id,
            title=returned_role.title,
            description=returned_role.description,
        )

    async def get_role_by_name(self, role_name: str) -> Role:
        result = await self.db.execute(select(RoleModel).where(RoleModel.title == role_name))
        returned_role = result.scalars().one_or_none()
        if returned_role is not None:
            return Role(
                id=returned_role.id,
                title=returned_role.title,
                description=returned_role.description,
            )
        else:
            return

    async def update_role(self, role_patch: Role) -> Role:
        logging.warn(role_patch.model_dump(exclude_none=True))
        query = (
            update(RoleModel)
            .where(RoleModel.id == str(role_patch.id))
            # .values(**role_patch.model_dump(exclude_none=True))
            .values(title=role_patch.title, description=role_patch.description)
            .returning(RoleModel)
        )
        result = await self.db.execute(query)
        updated_role = result.scalars().one_or_none()

        if not updated_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'role with id {role_patch.id} does not exist',
            )

        await self.db.commit()
        return role_patch

    async def delete_role(self, role_id: str):
        result = await self.db.execute(delete(RoleModel).where(RoleModel.id == role_id).returning(RoleModel))
        deleted_role = result.scalars().one_or_none()
        if deleted_role is None:
            return

        await self.db.commit()
        resp = Role(id=deleted_role.id, title=deleted_role.title, description=deleted_role.description)
        return resp


@lru_cache
def get_role_service(
        db: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(db=db)

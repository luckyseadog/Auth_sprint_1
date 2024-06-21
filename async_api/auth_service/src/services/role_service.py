from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select, update

from db.postgres_db import AsyncSession
from models.entity import RoleModel
from schemas.entity import Role
from schemas.entity_schemas import RolePatch


class RoleService():
    async def create_role(self, role_create: Role, db: AsyncSession) -> Role:
        role_dto = jsonable_encoder(role_create, exclude_none=True)
        role = RoleModel(**role_dto)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    async def get_roles(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Role]:
        result = await db.execute(select(RoleModel))
        return [
            Role(
                id=role.id,
                title=role.title,
                description=role.description,
            ) for role in result.scalars()
        ]

    async def get_role_by_id(self, role_id: str, db: AsyncSession) -> Role:
        result = await db.execute(select(RoleModel).where(RoleModel.id == role_id))
        returned_role = result.scalars().one_or_none()
        if returned_role is not None:
            return Role(
                id=returned_role.id,
                title=returned_role.title,
                description=returned_role.description,
            )
        else:
            return

    async def get_role_by_name(self, role_name: str, db: AsyncSession) -> Role:
        result = await db.execute(select(RoleModel).where(RoleModel.title == role_name))
        returned_role = result.scalars().one_or_none()
        if returned_role is not None:
            return Role(
                id=returned_role.id,
                title=returned_role.title,
                description=returned_role.description,
            )
        else:
            return

    async def update_role(self, role_id: str, role_patch: RolePatch, db: AsyncSession) -> Role:
        query = (
            update(RoleModel)
            .where(RoleModel.id == str(role_id))
            .values(**role_patch.model_dump(exclude_none=True))
            .returning(RoleModel)
        )
        result = await db.execute(query)
        updated_role = result.scalars().one_or_none()

        if updated_role is None:
            return

        await db.commit()
        return Role(
            id=updated_role.id,
            title=updated_role.title,
            description=updated_role.description,
        )

    async def delete_role(self, role_id: str, db: AsyncSession):
        result = await db.execute(delete(RoleModel).where(RoleModel.id == role_id).returning(RoleModel))
        deleted_role = result.scalars().one_or_none()

        if deleted_role is None:
            return

        await db.commit()
        return Role(
            id=deleted_role.id,
            title=deleted_role.title,
            description=deleted_role.description,
        )


role_service = RoleService()

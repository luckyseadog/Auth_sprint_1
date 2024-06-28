from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from schemas.entity import Role
from services.role_service import RoleService, get_role_service
from services.validation import check_admin_or_super_admin_role_from_access_token

router = APIRouter(
    dependencies=[Depends(check_admin_or_super_admin_role_from_access_token)],
)


@router.get(
    '/roles',
    response_model=list[Role],
    status_code=status.HTTP_200_OK,
    summary='Получение списка ролей',
    description='',
)
async def get_roles(
    role_service: Annotated[RoleService, Depends(get_role_service)],
    user_agent: Annotated[str | None, Header()] = None,
) -> list[Role]:
    return await role_service.get_roles()


@router.post(
    '/roles',
    response_model=Role,
    status_code=status.HTTP_200_OK,
    summary='Добавление роли',
    description='',
)
async def add_role(
    role_create: Role,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    user_agent: Annotated[str | None, Header()] = None,
):
    return await role_service.create_role(role_create=role_create)


@router.put(
    '/roles',
    response_model=Role,
    status_code=status.HTTP_200_OK,
    summary='Обновление роли',
    description='',
)
async def update_role(
    role_patch: Role,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    # user_agent: Annotated[str | None, Header()] = None,
) -> Role:
    return await role_service.update_role(role_patch)


@router.delete(
    '/roles',
    status_code=status.HTTP_200_OK,
    summary='Удаление роли',
    description='',
    response_model=Role,
)
async def delete_role(
    role_id: UUID,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    # user_agent: Annotated[str | None, Header()] = None,
):
    return await role_service.delete_role(role_id=str(role_id))

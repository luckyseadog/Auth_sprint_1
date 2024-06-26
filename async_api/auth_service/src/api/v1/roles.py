from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from schemas.entity import History, Role
from schemas.entity_schemas import AccessTokenData
from services.history_service import HistoryService, get_history_service
from services.role_service import RoleService, get_role_service
from services.user_service import UserService, get_user_service
from services.validation import \
    check_admin_or_super_admin_role_from_access_token

router = APIRouter()


@router.get(
    '/roles',
    response_model=list[Role],
    status_code=status.HTTP_200_OK,
    summary='Получение списка ролей',
    description='',
)
async def get_roles(
    role_service: Annotated[RoleService, Depends(get_role_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    payload: Annotated[AccessTokenData, Depends(check_admin_or_super_admin_role_from_access_token)],
    user_agent: Annotated[str | None, Header()] = None,
) -> list[Role]:
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )
    
    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/roles[GET]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

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
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    payload: Annotated[AccessTokenData, Depends(check_admin_or_super_admin_role_from_access_token)],
    user_agent: Annotated[str | None, Header()] = None,
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )

    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/roles[ADD]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

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
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    payload: Annotated[AccessTokenData, Depends(check_admin_or_super_admin_role_from_access_token)],
    user_agent: Annotated[str | None, Header()] = None,
) -> Role:
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )
    
    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/roles[UPDATE]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    return await role_service.update_role(role_patch)


@router.delete(
    '/roles',
    status_code=status.HTTP_200_OK,
    summary='Удаление роли',
    description='',
)
async def delete_role(
    role_id: UUID,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    payload: Annotated[AccessTokenData, Depends(check_admin_or_super_admin_role_from_access_token)],
    user_agent: Annotated[str | None, Header()] = None,
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )
    
    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/roles[DELETE]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    return await role_service.delete_role(role_id=str(role_id))

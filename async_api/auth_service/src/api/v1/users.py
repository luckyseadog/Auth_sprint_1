from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import ORJSONResponse

from core.config import settings
from schemas.entity import History, User
from schemas.entity_schemas import AccessTokenData
from services.user_service import UserService, get_user_service
from services.history_service import HistoryService, get_history_service
from services.validation import (
    validate_access_token,
    # check_admin_or_super_admin_role_from_access_token,
    get_current_active_user,
    check_admin_or_super_admin_role,
)


router = APIRouter()


@router.get(
    path='/users',
    # response_model=list[User],
    status_code=status.HTTP_200_OK,
    summary='Получение списка пользователей',
    description='Получить список пользователй из БД',
    dependencies=[Depends(check_admin_or_super_admin_role)],
)
async def get_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    # user_agent: Annotated[str | None, Header()] = None,
):
    users = await user_service.get_users()
    return users


@router.put(
    path='/users',
    status_code=status.HTTP_200_OK,
    summary='Добавление пользователя',
    description='Добавление пользователя в БД',
    response_model=User,
    dependencies=[Depends(get_current_active_user)],
)
async def change_user(
    user_patch: User,
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )

    db_user = await user_service.update_user(user_patch)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    return db_user


@router.delete(
    path='/users',
    description='Удаление пользователя',
    summary='Удаление пользователя из БД',
    response_model=User,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: str,
    response: ORJSONResponse,
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
    # payload_admin: AccessTokenData = Depends(check_admin_or_super_admin_role_from_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with admin role was deleted',
        )

    db_user = await user_service.delete_user(user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    response.delete_cookie(key=settings.access_token_name)
    response.delete_cookie(key=settings.refresh_token_name)

    return db_user


@router.get(
    path='/users/history',
    description='Получение истории операций пользователя',
    summary='История входа/выхода пользователя',
    response_model=list[History],
    status_code=status.HTTP_200_OK,

)
async def get_history(
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
) -> list[History]:
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )

    user_history = await history_service.get_last_user_notes(payload.sub)
    return user_history


@router.get(
    '/users/me',
    response_model=User,
    description='Текущий пользователь',
    summary='Информация о текущем пользователе',
    status_code=status.HTTP_200_OK,
)
async def get_me(
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )

    user = await user_service.get_user(payload.sub)
    return user

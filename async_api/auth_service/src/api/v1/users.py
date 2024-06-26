from typing import Annotated

from core.config import settings
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import ORJSONResponse
from schemas.entity import History, User
from schemas.entity_schemas import AccessTokenData
from services.history_service import HistoryService, get_history_service
from services.user_service import UserService, get_user_service
from services.validation import (
    check_admin_or_super_admin_role_from_access_token, validate_access_token)

router = APIRouter()

@router.get(
    path='/users',
    response_model=list[User],
    status_code=status.HTTP_200_OK,
    summary='Получение списка пользователей',
    description='Получить список пользователй из БД',
)
async def get_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(check_admin_or_super_admin_role_from_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )

    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/users[GET]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    users = await user_service.get_users()
    return users


@router.put('/users')
async def change_user(
    user_patch: User,
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )
    
    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/users[CHANGE]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    db_user = await user_service.update_user(user_patch)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    return db_user


@router.delete('/users')
async def delete_user(
    response: ORJSONResponse,
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
    # payload_admin: AccessTokenData = Depends(check_admin_or_super_admin_role_from_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with admin role was deleted',
        )

    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/users[DELETE]',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    db_user = await user_service.delete_user(payload.sub)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    response.delete_cookie(key=settings.access_token_name)
    response.delete_cookie(key=settings.refresh_token_name)

    return db_user


@router.get('/users/history')
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

    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/users/history',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    user_history = await history_service.get_last_user_notes(payload.sub)
    return user_history


@router.get(
    '/users/me',
    response_model=User,
)
async def get_me(
    user_service: Annotated[UserService, Depends(get_user_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    user_agent: Annotated[str | None, Header()] = None,
    payload: AccessTokenData = Depends(validate_access_token),
):
    if await user_service.is_deleted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User was deleted',
        )

    user_id = payload.sub
    note = History(
            user_id=(str(user_id)),
            action='/users/me',
            fingerprint=user_agent,
        )
    await history_service.make_note(note)

    user = await user_service.get_user(payload.sub)
    return user

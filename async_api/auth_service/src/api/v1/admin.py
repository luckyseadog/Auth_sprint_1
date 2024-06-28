from typing import Annotated

from fastapi import APIRouter, Depends, status

from schemas.entity import User
from schemas.entity_schemas import UpdateUserRole
from services.validation import check_admin_or_super_admin_role_from_access_token
from services.admin_service import AdminService, get_admin_service

router = APIRouter(
    dependencies=[Depends(check_admin_or_super_admin_role_from_access_token)],
)


@router.post(
    '/user_role/assign',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Назначение роли пользователю',
    description='''
    В теле запроса принимает два параметра: uuid пользователя и uuid роли.
    - Если у пользователяю роль присутствует ничего не происходит.\n
    - Если у пользователя нет роли, то она добавляется.\n
    - Если нет такого пользователя возвращается ошибка 404 с описанием что такого пользователя нет.\n
    - Если нет такой роли - возвращаетс ошибка 404 с описаниме, что нет такой роли.\n
    ''',
)
async def assign_role(
    user_role: UpdateUserRole,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
) -> User:
    updated_user = await admin_service.assign_user_role(str(user_role.user_id), str(user_role.role_id))
    return updated_user


@router.post(
    '/user_role/revoke',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Отзыв роли у пользователя',
    description='',
)
async def revoke_role(
    user_role: UpdateUserRole,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
) -> User:
    return await admin_service.revoke_user_role(str(user_role.user_id), str(user_role.role_id))


@router.post(
    '/user_role/check',
    status_code=status.HTTP_200_OK,
    summary='Проверка наличия роли у пользователя',
    description='',
)
async def check_role(
    user_role: UpdateUserRole,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    # user_agent: Annotated[str | None, Header()] = None,
):
    res = await admin_service.check_user_role(str(user_role.user_id), str(user_role.role_id))
    return {'result': 'YES' if res else 'NO'}

from typing import Annotated, Union

from fastapi import APIRouter, Cookie, Depends, Header, status
from fastapi.responses import ORJSONResponse
from fastapi.security.oauth2 import (
    OAuth2PasswordRequestForm,
)

from core.config import settings
from schemas.entity_schemas import (
    AccessTokenData, RefreshTokenData,
    TokenPair, UserCreate, UserCredentials,
)
from schemas.entity import User

from services.user_service import UserService, get_user_service
from services.auth_service import AuthService, get_auth_service
from services.role_service import RoleService, get_role_service
from services.validation import validate_access_token, validate_refresh_token, check_origin
from uuid import uuid4

router = APIRouter()


@router.post(
    path='/signup',
    # response_model=,
    status_code=status.HTTP_200_OK,
    summary='Регистрация пользователя',
    description='''
    Ручка позволяет зарегистрироваться новому пользователю\n
    В теле запроса необходимо предать:
    - login
    - password
    - first_name
    - last_name
    - email

    'Уникальными полями явлюятся: имя пользователя (login) и почта (email).
    'Если пользователь с таким логином и почтой уже существует возвращается ошибка 409 с описанием,
    'что такой пользователь уже существует.\n''
    ''',
    response_model=User,
    dependencies=[Depends(check_origin)],
)
async def signup(
    user_create: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
    # response: ORJSONResponse,
):
    return await user_service.create_user(user_create)


@router.post(
    '/login',
    # response_model=,
    status_code=status.HTTP_200_OK,
    response_model=TokenPair,
    summary='Аутентификация пользователя',
    description='''
    В теле запроса принимает два параметра: логин и пароль.
    Если пользователь аутентифицирован, вернуть его токены, если такого пользователя не
    существует или неверный пароль вернуть 401
    ''',
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: ORJSONResponse,
    # origin: Annotated[str | None, Header()] = None,
    origin: Annotated[str, Depends(check_origin)],
    user_agent: Annotated[str | None, Header()] = None,
) -> TokenPair:

    user_creds = UserCredentials(login=form_data.username, password=form_data.password)
    tokens = await auth_service.login(user_creds, origin=origin, user_agent=user_agent)

    response.set_cookie(
        key=settings.access_token_name,
        value=tokens.access_token,
        httponly=True,
        expires=tokens.access_exp,
    )

    response.set_cookie(
        key=settings.refresh_token_name,
        value=tokens.refresh_token,
        httponly=True,
        expires=tokens.refresh_exp,
    )

    return TokenPair(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,

    )


@router.post(
    '/logout',
    # response_model=,
    status_code=status.HTTP_200_OK,
    summary='Выход пользователя',
    description='Из токена получается id пользователя. '
                'Токен помещается в кеш забаненнных access токенов. '
                'Если пользователь решит снова аутентифицироваться, то ему придётся ввести логин и пароль.',
)
async def logout(
    response: ORJSONResponse,
    payload: Annotated[AccessTokenData, Depends(validate_access_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: Annotated[Union[str, None], Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):
    user_id = payload.sub
    response.delete_cookie(key=settings.access_token_name)
    response.delete_cookie(key=settings.refresh_token_name)
    return await auth_service.logout(user_id, access_token, user_agent)

#
#
@router.post(
    '/logout_all',
    # response_model=,
    status_code=status.HTTP_200_OK,
    summary='Выход пользователя из всех устройств',
    description='',
)
async def logout_all(
    response: ORJSONResponse,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    payload: Annotated[AccessTokenData, Depends(validate_access_token)],
    user_agent: Annotated[str | None, Header()] = None,

):
    await auth_service.logout_all(payload.sub, user_agent)
    response.delete_cookie(key=settings.access_token_name)
    response.delete_cookie(key=settings.refresh_token_name)
    return {'message': 'All accounts deactivated'}


@router.post(
    '/refresh',
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary='Обновление access и refresh токенов',
    description='',
)
async def refresh(
    response: ORJSONResponse,
    payload: Annotated[RefreshTokenData, Depends(validate_refresh_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    origin: Annotated[str | None, Header()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):

    user_id = payload.sub
    tokens = await auth_service.refresh(user_id, origin, user_agent)

    response.set_cookie(
        key=settings.access_token_name,
        value=tokens.access_token,
        httponly=True,
        expires=tokens.access_exp,
    )

    response.set_cookie(
        key=settings.refresh_token_name,
        value=tokens.refresh_token,
        httponly=True,
        expires=tokens.refresh_exp,
    )

    return TokenPair(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )
#
#
@router.post(
    '/signup_guest',
    # response_model=,
    status_code=status.HTTP_200_OK,
    summary='Регистрация гостевого пользователя',
    description='''
    В теле запроса принимает два параметра: логин и пароль.
    - Если пользователь с таким логином уже существует возвращается ошибка 409 с
    описанием что такой пользователь уже существует.\n
    - Если пользователь с таким логином не существует, то он добавляется.\
    ''',
)
async def signup_guest(
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    response: ORJSONResponse,
    origin: Annotated[str | None, Header()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):

    role = await role_service.get_role_by_name(settings.role_guest)
    new_user_id = str(uuid4())
    guest_create = User(
        id=new_user_id,
        login=f'guest_{new_user_id}',
        email=f'email_{new_user_id}@auth.com',
        password=new_user_id,
        first_name=f'first_name_{new_user_id}',
        last_name=f'last_name_{new_user_id}',
        roles=[role],
    )

    await user_service.create_user(guest_create)
    user_creds = UserCredentials(login=guest_create.login, password=new_user_id)
    tokens = await auth_service.login(user_creds, origin=origin, user_agent=user_agent)

    response.set_cookie(
        key=settings.access_token_name,
        value=tokens.access_token,
        httponly=True,
        expires=tokens.access_exp,
    )

    response.set_cookie(
        key=settings.refresh_token_name,
        value=tokens.refresh_token,
        httponly=True,
        expires=tokens.refresh_exp,
    )

    return TokenPair(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,

    )

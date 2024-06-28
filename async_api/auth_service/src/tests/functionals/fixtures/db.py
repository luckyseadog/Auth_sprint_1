import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, AsyncEngine, AsyncConnection,
)
from uuid import uuid4
from tests.settings import settings
from db.postgres_db import Base
from models.entity import RoleModel, UserModel, UserRoleModel
from services.password_service import password_service

import json
import os


@pytest_asyncio.fixture(scope='session')
async def async_engine() -> AsyncEngine:
    DSN = (
        f'postgresql+asyncpg://{settings.pg_user}:{settings.pg_pass}'
        f'@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}'
    )
    return create_async_engine(DSN, echo=False, future=True)


@pytest_asyncio.fixture(scope='function')
async def prepare_database(async_engine: AsyncEngine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='session')
async def async_connection(async_engine: AsyncEngine) -> AsyncConnection:
    async with async_engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture(scope='session')
async def async_session(async_connection: AsyncConnection):
    async with AsyncSession(bind=async_connection) as session:
        yield session


@pytest_asyncio.fixture(scope='function')
async def roles_in_db(async_session: AsyncSession):
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/../testdata/data/roles.json') as file:
        for item in json.load(file):
            role = RoleModel(
                id=item['id'],
                title=item['title'],
                description=item['description'],
            )
            async_session.add(role)
        await async_session.flush()
        await async_session.commit()


@pytest_asyncio.fixture(scope='function')
async def users_in_db(async_session: AsyncSession):
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/../testdata/data/users.json') as file:
        data = json.load(file)
        for item in data[:10]:
            user = UserModel(
                id=item['id'],
                login=item['login'],
                password=password_service.compute_hash(item['password']),
                email=item['email'],
                first_name=item['first_name'],
                last_name=item['last_name'],
            )
            async_session.add(user)
        await async_session.flush()
        await async_session.commit()

        # data = json.load(file)
        #             for item in data:
        #                 user = UserModel(
        #                     id=item['id'],
        #                     login=item['login'],
        #                     password=password_service.compute_hash(item['password']),
        #                     email=item['email'],
        #                     first_name=item['first_name'],
        #                     last_name=item['last_name'],
        #                 )
        #                 async_session.add(user)


@pytest_asyncio.fixture(scope='function')
async def super_admin(async_session: AsyncSession):
    role_id = str(uuid4())
    user_id = str(uuid4())

    role = RoleModel(
        id=role_id,
        title=settings.role_super_admin,
        description=f'{settings.role_super_admin} description',
    )
    async_session.add(role)
    await async_session.flush()

    user = UserModel(
        id=user_id,
        login=settings.sa_login,
        password=password_service.compute_hash(settings.sa_password),
        email=settings.sa_email,
        first_name=settings.sa_firstname,
        last_name=settings.sa_lastname,
    )
    async_session.add(user)
    await async_session.flush()

    user_role = UserRoleModel(user_id=user_id, role_id=role_id)
    async_session.add(user_role)
    await async_session.commit()


# @pytest_asyncio.fixture(scope='session')
# async def fill_db(async_session: AsyncSession):
#     with open(f'{os.path.dirname(os.path.realpath(__file__))}/../testdata/data/roles.json') as file:
#         for item in json.load(file):
#             role = RoleModel(
#                 id=item['id'],
#                 title=item['title'],
#                 description=item['description'],
#             )
#             async_session.add(role)
#         await async_session.flush()
#
#         with open(f'{os.path.dirname(os.path.realpath(__file__))}/../testdata/data/users.json') as file:
#             data = json.load(file)
#             for item in data:
#                 user = UserModel(
#                     id=item['id'],
#                     login=item['login'],
#                     password=password_service.compute_hash(item['password']),
#                     email=item['email'],
#                     first_name=item['first_name'],
#                     last_name=item['last_name'],
#                 )
#                 async_session.add(user)
#
#                 for role in item['roles']:
#                     user_role = UserRoleModel(user_id=item['id'], role_id=role['id'])
#                     async_session.add(user_role)
#             await async_session.flush()
#
#             for item in data:
#                 for history in item['history']:
#                     user_history = UserHistoryModel(
#                         user_id=item['id'],
#                         occured_at=datetime.strptime(history['occured_at'], '%Y-%m-%d %H:%M:%S'),
#                         action=history['action'],
#                         fingerprint=history['fingerprint'],
#
#                     )
#                     async_session.add(user_history)
#             await async_session.flush()
#         await async_session.commit()
    # yield
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

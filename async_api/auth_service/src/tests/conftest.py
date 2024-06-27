import asyncio

from httpx import ASGITransport
import pytest_asyncio
import httpx
from main import app
from tests.settings import settings


pytest_plugins = (
    'tests.functionals.fixtures.db',
)

@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client():
    async with httpx.AsyncClient(transport=ASGITransport(app), base_url=settings.root_path) as client:
        yield client


@pytest_asyncio.fixture(scope='function')
async def superadmin_cookies(prepare_database, super_admin, client):
    response = await client.post(
        '/login', data={
            'username': settings.sa_login,
            'password': settings.sa_password,
        },
        headers={'Origin': settings.root_path},
    )
    yield response.cookies


# @pytest_asyncio.fixture(scope='session')
# async def prepare_database():
#     DSN = (
#         f'postgresql+asyncpg://{settings.pg_user}:{settings.pg_pass}'
#         f'@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}'
#     )
#     engine = create_async_engine(DSN, echo=False, future=True)
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture(scope='session')
# async def prepare_database():
#     DSN = (
#         f'postgresql+asyncpg://{settings.pg_user}:{settings.pg_pass}'
#         f'@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}'
#     )
#     engine = create_async_engine(DSN, echo=True, future=True)
#     async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     async with async_session() as session:
#         with open(f'{os.path.dirname(os.path.realpath(__file__))}/functionals/testdata/data/roles.json') as file:
#             for item in json.load(file):
#                 role = RoleModel(
#                     id=item['id'],
#                     title=item['title'],
#                     description=item['description'],
#                 )
#                 session.add(role)
#             await session.flush()
#
#         with open(f'{os.path.dirname(os.path.realpath(__file__))}/functionals/testdata/data/users.json') as file:
#             data = json.load(file)
#             for item in data:
#                 user = UserModel(
#                     id=item['id'],
#                     login=item['login'],
#                     password=item['password'],
#                     email=item['email'],
#                     first_name=item['first_name'],
#                     last_name=item['last_name'],
#                 )
#                 session.add(user)
#                 print(item['roles'])
#
#                 for role in item['roles']:
#                     user_role = UserRoleModel(user_id=item['id'], role_id=role['id'])
#                     session.add(user_role)
#             await session.flush()
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
#                     session.add(user_history)
#             await session.flush()
#         await session.commit()
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')

    pg_db: str = Field('auth_database', alias='PG_NAME')
    pg_host: str = Field('127.0.0.1', alias='PG_HOST')
    pg_port: int = Field(5432, alias='PG_PORT')
    pg_user: str = Field('app', alias='PG_USER')
    pg_pass: str = Field('123qwe', alias='PG_PASSWORD')

    root_path: str = Field('http://localhost:8000/api/v1/auth', alias='ROOT_PATH')

    sa_login: str = Field('superadmin', alias='SUPER_USER_LOGIN')
    sa_password: str = Field('admin', alias='SUPER_USER_PASSWORD')
    sa_firstname: str = Field('admin', alias='SUPER_USER_FIRST_NAME')
    sa_lastname: str = Field('admin', alias='SUPER_USER_LAST_NAME')
    sa_email: str = Field('superadmin@admin.com', alias='SUPER_USER_EMAIL')

    role_admin: str = Field('admin', alias='ADMIN_ROLE_NAME')
    role_super_admin: str = Field('superadmin', alias='SUPERADMIN_ROLE_NAME')
    role_user: str = Field('user', alias='USER_ROLE_NAME')
    role_subscriber: str = Field('subscriber', alias='SUBSCRIBER_ROLE_NAME')
    role_guest: str = Field('guest', alias='GUEST_ROLE_NAME')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()

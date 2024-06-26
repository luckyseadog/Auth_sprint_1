import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    project_name: str = 'movies'
    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')

    elastic_host: str = Field('127.0.0.1', alias='ELASTIC_HOST')
    elastic_port: int = Field(9200, alias='ELASTIC_PORT')

    pg_user: str = Field('app', alias='AUTH_DB_USER')
    pg_host: str = Field('127.0.0.1', alias='AUTH_HOST')
    pg_port: int = Field(5432, alias='AUTH_DB_PORT')
    pg_password: str = Field('123qwe', alias='AUTH_DB_PASSWORD')
    pg_name: str = Field('auth_database', alias='AUTH_DB_NAME')

    secret_key: str = Field('secret', alias='SECRET_KEY')
    algorithm: str = Field('HS256', alias='ALGORITHM')

    access_token_min: int = Field(15, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_weeks: int = Field(1, alias='REFRESH_TOKEN_WEEKS')

    sa_login: str = Field('superadmin', alias='SUPER_USER_LOGIN')
    sa_password: str = Field('admin', alias='SUPER_USER_PASSWORD')
    sa_firstname: str = Field('admin', alias='SUPER_USER_FIRST_NAME')
    sa_lastname: str = Field('admin', alias='SUPER_USER_LAST_NAME')
    sa_email: str = Field('superadmin@admin.com', alias='SUPER_USER_EMAIL')

    sec_salt: str = Field('<salt>', alias='SALT')
    sec_app_iters: int = Field(100_000, alias='APP_ITERS')

    role_admin: str = Field('admin', alias='ADMIN_ROLE_NAME')
    role_super_admin: str = Field('superadmin', alias='SUPERADMIN_ROLE_NAME')
    role_user: str = Field('user', alias='USER_ROLE_NAME')
    role_subscriber: str = Field('subscriber', alias='SUBSCRIBER_ROLE_NAME')
    role_guest: str = Field('guest', alias='GUEST_ROLE_NAME')
    role_admin_descripiton: str = Field('admin_descripiton', alias='SUPERADMIN_ROLE_DESCRIPTION')

    access_token_name: str = Field('access_token', alias='ACCESS_TOKEN')
    refresh_token_name: str = Field('refresh_token', alias='REFRESH_TOKEN')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()

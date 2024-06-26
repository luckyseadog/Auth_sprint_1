import uuid
from datetime import datetime

from db.postgres_db import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship


class RoleModel(Base):
    __tablename__ = 'roles'

    id = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = mapped_column(String(255), unique=True, nullable=False, index=True)
    description = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime, default=datetime.now)
    updated_at = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    users = relationship('UserModel', secondary='users_roles', back_populates='roles', lazy='selectin')

    def __repr__(self):
        return f'<RoleModel {self.title}>'


class UserModel(Base):
    __tablename__ = 'users'

    id = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    login = mapped_column(String(255), unique=True, nullable=False, index=True)
    password = mapped_column(String(255), nullable=False)
    first_name = mapped_column(String(50), nullable=False)
    last_name = mapped_column(String(50), nullable=False)
    email = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = mapped_column(DateTime, nullable=True, default=None)  # TODO: rename to is_deleted
    is_superadmin = mapped_column(Boolean, default=False)
    roles = relationship('RoleModel', secondary='users_roles', back_populates='users', lazy='selectin')

    def __repr__(self) -> str:
        return f'<UserModel {self.login}>'


class UserHistoryModel(Base):
    __tablename__ = 'user_history'

    id = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = mapped_column(String, ForeignKey('users.id'))
    occured_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    action = mapped_column(String(255), nullable=False)
    fingerprint = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f'<UserHistoryModel {self.user_id} - {self.action}>'


class UserRoleModel(Base):
    __tablename__ = 'users_roles'

    id = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = mapped_column(String, ForeignKey('users.id'))
    role_id = mapped_column(String, ForeignKey('roles.id'))
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

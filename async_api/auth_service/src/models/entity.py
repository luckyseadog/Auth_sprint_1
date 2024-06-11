import uuid
import time

from sqlalchemy.orm import mapped_column
from sqlalchemy import Boolean, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase
from db.postgres import Base


class Base(DeclarativeBase):
    pass


class UserRole(Base):
    __tablename__ = 'users_roles'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id= mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    role_id = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"))
    updated_at = mapped_column(DateTime, default=time.time(), onupdate=time.time())


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = mapped_column(String(255), unique=True, nullable=False)
    password = mapped_column(String(255), nullable=False)
    first_name = mapped_column(String(50), nullable=False)
    last_name = mapped_column(String(50), nullable=False)
    email = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime, default=time.time)
    updated_at = mapped_column(DateTime, default=time.time, onupdate=time.time)
    deleted_at = mapped_column(Boolean, default=True) #TODO: rename to is_deleted
    # is_superadmin = Column(Boolean, default=False)
    roles = relationship("Role", secondary='users_roles', back_populates='users', lazy='selectin')

    # history = relationship("History", secondary=)


    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Role(Base):
    __tablename__ = 'roles'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = mapped_column(String(255), unique=True, nullable=False)
    description = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime, default=time.time)
    updated_at = mapped_column(DateTime, default=time.time, onupdate=time.time)
    users = relationship("User", secondary='users_roles', back_populates='roles', lazy='selectin')

    def __repr__(self):
        return f'<Role {self.title}>'

class UserHistory(Base):
    __tablename__ = 'user_history'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    occured_at = mapped_column(DateTime, default=time.time, onupdate=time.time)
    action = mapped_column(String(255), nullable=False)
    fingreprint = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f'<UserHistory {self.user_id} - {self.action}>'
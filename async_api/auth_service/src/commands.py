import typer
from core.config import settings
from models.entity import RoleModel, UserModel
from services.password_service import PasswordService
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

app = typer.Typer()

dsn = (
    f'postgresql+psycopg://{settings.pg_user}'
    f':{settings.pg_password}@{settings.pg_host}'
    f':{settings.pg_port}/{settings.pg_name}'
)


engine = create_engine(dsn, echo=True, future=True)


def create_role(title: str, description: str):
    with Session(engine) as session:
        role = session.scalars(select(RoleModel).where(RoleModel.title == title)).one_or_none()
        if role:
            return

        role = RoleModel(title=title, description=description)
        session.add(role)
        session.commit()


def create_superadmin_user():
    with Session(engine) as session:
        user = session.scalars(select(UserModel).where(UserModel.login == settings.sa_login)).one_or_none()
        if user:
            return

        pass_service = PasswordService()
        superadmin = UserModel(
            login=settings.sa_login,
            email=settings.sa_email,
            first_name=settings.sa_firstname,
            last_name=settings.sa_lastname,
            password=pass_service.compute_hash(settings.sa_password),
            is_superadmin=True,
        )
        session.add(superadmin)
        session.commit()


def assign_superadmin_role_to_superadmin():
    with Session(engine) as session:
        superadmin_user = session.scalars(select(UserModel).where(UserModel.login == settings.sa_login)).one()
        superadmin_role = session.scalars(select(RoleModel).where(RoleModel.title == settings.role_super_admin)).one()
        superadmin_user.roles.append(superadmin_role)
        session.commit()


@app.command()
def create_superadmin():
    create_role(title=settings.role_super_admin, description='superadmin role description')
    create_superadmin_user()
    assign_superadmin_role_to_superadmin()


@app.command()
def delete_superadmin():
    with Session(engine) as session:
        user = session.scalars(select(UserModel).where(UserModel.login == settings.sa_login)).one_or_none()
        if user:
            session.delete(user)
            session.commit()


@app.command()
def create_roles():
    create_role(title=settings.role_admin, description='admin role description')
    create_role(title=settings.role_subscriber, description='subscriber role description')
    create_role(title=settings.role_guest, description='guest role description')
    create_role(title=settings.role_user, description='user role description')


if __name__ == '__main__':
    app()

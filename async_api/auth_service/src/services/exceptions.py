from fastapi import HTTPException, status


def role_not_found(role_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Role with id {role_id} not found',
    )


def user_not_found(user_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Role with id {user_id} not found',
    )


def role_already_exists(role_id: str) -> HTTPException:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f'role {role_id} already exists',
    )

def role_not_exists(role_id: str) -> HTTPException:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f'role {role_id} not exists in user',
    )

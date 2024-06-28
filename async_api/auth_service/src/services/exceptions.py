from fastapi import HTTPException, status


def role_not_found(role_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Role with id {role_id} not found',
    )

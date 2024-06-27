from pydantic import BaseModel
from typing import Union
from fastapi import APIRouter, status

router = APIRouter()

class User(BaseModel):
    fullName: str
    email: str
    password: str
    nif: str
    type: int

class UserUpdate(BaseModel):
    fullName: Union[str, None] = None
    email: Union[str, None] = None
    nif: Union[str, None] = None
    type: Union[int, None] = None


@router.get('/status')
def get_admin_status(admin_id: str, session_id: str):
    from api.admin import get_admin_status
    return get_admin_status(admin_id, session_id)

@router.get('/users', status_code=status.HTTP_200_OK)
def get_users(admin_id: str, session_id: str):
    from api.admin import get_users
    return get_users(admin_id, session_id)

@router.post('/users', status_code=status.HTTP_201_CREATED)
def create_user(admin_id: str, session_id: str , user: User):
    from api.admin import create_user
    user.email = user.email.lower()
    user.fullName = user.fullName.title()
    return create_user(admin_id, session_id, user)

@router.put('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED)
def update_user(user_id: str, admin_id, session_id: str, user: UserUpdate):
    from api.admin import update_user
    if user.email:
        user.email = user.email.lower()
    if user.fullName:
        user.fullName = user.fullName.title()
    return update_user(user_id, admin_id, session_id, user)

@router.delete('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_user(user_id: str, admin_id, session_id: str):
    from api.admin import delete_user
    return delete_user(user_id, admin_id, session_id)

@router.patch('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED)
def restore_user(user_id: str, admin_id, session_id: str):
    from api.admin import restore_user
    return restore_user(user_id, admin_id, session_id)

@router.patch('/ban/{user_id}', status_code=status.HTTP_202_ACCEPTED)
def ban_user(user_id: str, admin_id, session_id: str):
    from api.admin import ban_user
    return ban_user(user_id, admin_id, session_id)

@router.patch('/unban/{user_id}', status_code=status.HTTP_200_OK)
def unban_user(user_id: str, admin_id, session_id: str):
    from api.admin import unban_user
    return unban_user(user_id, admin_id, session_id)
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

@router.patch('/users/{user_id}/{perm}', status_code=status.HTTP_202_ACCEPTED)
def update_user(user_id: str, perm: int, admin_id, session_id: str):
    from api.admin import update_user_perms
    return update_user_perms(user_id, perm, admin_id, session_id)

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

@router.get('/users/{search}', status_code=status.HTTP_200_OK)
def get_user(search: str, admin_id, session_id: str):
    from api.admin import search_user
    return search_user(search, admin_id, session_id)

@router.get('/requests', status_code=status.HTTP_200_OK)
def get_request_to_approve(admin_id, session_id):
    from api.admin import get_request_to_approve
    return get_request_to_approve(admin_id, session_id)

class Fire(BaseModel):
    date: str
    typeId: int
    reasonId: int
    zipCodeId: int
    location: Union[str, None] = None
    observations: Union[str, None] = None

@router.post('/fire', status_code=status.HTTP_201_CREATED)
def create_fire(admin_id: str, session_id: str, user_id: str, fire: Fire):
    from api.admin import create_fire
    return create_fire(admin_id, session_id, user_id, fire)
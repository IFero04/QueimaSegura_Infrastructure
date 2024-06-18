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
    user = user.dict(exclude_none=True)
    return update_user(user_id, admin_id, session_id, user)
from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()

class User(BaseModel):
    fullName: str
    email: str
    password: str
    nif: str

class UserUpdate(BaseModel):
    fullName: str
    email: str
    nif: str


@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    from api.users import create_user
    user.email = user.email.lower()
    user.fullName = user.fullName.title()
    return create_user(user)

@router.put('/update/{user_id}', status_code=status.HTTP_202_ACCEPTED)
def update_user(user_id: str, session_id: str, user: UserUpdate):
    from api.users import update_user
    user.email = user.email.lower()
    user.fullName = user.fullName.title()
    return update_user(user_id, session_id, user)

@router.get('/{user_id}', status_code=status.HTTP_200_OK)
def get_user(user_id: str, session_id: str):
    from api.users import get_user
    return get_user(user_id, session_id)

@router.get('/status/{user_id}', status_code=status.HTTP_200_OK)
def get_user_status(user_id: str, session_id: str):
    from api.users import get_user_status
    return get_user_status(user_id, session_id)
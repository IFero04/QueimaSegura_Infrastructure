from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()

class User(BaseModel):
    fullName: str
    email: str
    password: str
    nif: str
    type: int

@router.post('/users/create/{admin_id}/{session_id}', status_code=status.HTTP_201_CREATED)
def create_user(admin_id: str, session_id: str , user: User):
    from api.admin import create_user
    user.email = user.email.lower()
    user.fullName = user.fullName.title()
    return create_user(admin_id, session_id, user)
from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()

class LoginCredentials(BaseModel):
    email: str
    password: str


@router.get('/check_email/', status_code=status.HTTP_200_OK)
def check_email(email: str):
    from api.auth import valid_email
    email = email.lower()
    return valid_email(email)

@router.get('/check_session/', status_code=status.HTTP_200_OK)
def check_session(user_id: str, session_id: str):
    from util.check_authenticity import check_session
    return check_session(user_id, session_id)

@router.post('/login/', status_code=status.HTTP_202_ACCEPTED)
def login(credentials: LoginCredentials):
    from api.auth import login
    credentials.email = credentials.email.lower()
    return login(credentials)

@router.delete('/logout/', status_code=status.HTTP_202_ACCEPTED)
def logout(user_id: str, session_id: str):
    from api.auth import logout
    return logout(user_id, session_id)
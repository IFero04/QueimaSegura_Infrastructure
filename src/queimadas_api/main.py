import time
import nltk
from typing import Union, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from util.db import check_db
from util.config import settings

nltk.download('stopwords')

print("Loading DataBase ...")
while not check_db(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password):
    print("Retrying in 15 seconds ...")
    time.sleep(15)

print("DataBase loaded.")
app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK, tags=['root'])
def read_root():
    return {"apiName": settings.app_name}

# AUTH
class LoginCredentials(BaseModel):
    email: str
    password: str

@app.post('/auth/check_email/', status_code=status.HTTP_200_OK, tags=['auth'])
def check_email(email: str):
    from api.users import valid_email
    return valid_email(email)

@app.post('/auth/check_session/', status_code=status.HTTP_200_OK, tags=['auth'])
def check_session(user_id: str, session_id: str):
    from api.auth import check_session
    return check_session(user_id, session_id)

@app.post('/login/', status_code=status.HTTP_202_ACCEPTED ,tags=['auth'])
def login(credentials: LoginCredentials):
    from api.users import login
    return login(credentials)

@app.delete('/logout/', status_code=status.HTTP_202_ACCEPTED, tags=['auth'])
def logout(user_id: str, session_id: str):
    from api.users import logout
    return logout(user_id, session_id)


# USERS
class User(BaseModel):
    fullName: str
    email: str
    password: str
    nif: str

## TEMP 
@app.get('/users/', status_code=status.HTTP_200_OK, tags=['users'])
def get_users():
    from api.users import get_users
    return get_users()

# USERS
@app.post('/users/', status_code=status.HTTP_201_CREATED, tags=['users'])
def create_user(user: User):
    from api.users import create_user
    return create_user(user)

@app.put('/users/{user_id}/{session_id}/', status_code=status.HTTP_202_ACCEPTED, tags=['users'])
def update_user(user_id: str, session_id: str, user: User):
    from api.users import update_user
    return update_user(user_id, session_id, user)

# LOCATION
@app.get('/location/', status_code=status.HTTP_202_ACCEPTED, tags=['location'])
def get_location(search: str):
    from api.location import handle_location_response
    return handle_location_response(search)

# FIRES
class Fire(BaseModel):
    date: str
    typeId: int
    reasonId: int
    zipCodeId: int
    location: Union[str, None] = None
    observations: Union[str, None] = None

@app.post('/fires/{user_id}/{session_id}/', status_code=status.HTTP_201_CREATED, tags=['fires'])
def new_fire(user_id: str, session_id: str, fire: Fire):
    from api.fires import create_fire
    return create_fire(user_id, session_id, fire)

@app.get('/fires/{user_id}/{session_id}/', status_code=status.HTTP_200_OK, tags=['fires'])
def get_fires_by_user(user_id: str, session_id: str):
    from api.fires import get_user_fires
    return get_user_fires(user_id, session_id)
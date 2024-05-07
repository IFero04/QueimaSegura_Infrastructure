import time
from typing import Union
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from util.db import check_db
from util.config import settings

print("Loading DataBase ...")
while not check_db(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password):
    print("Retrying in 15 seconds ...")
    time.sleep(15)

print("DataBase loaded.")
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": settings.app_name}

# USERS
class User(BaseModel):
    full_name: str
    email: str
    password: str
    NIF: str

@app.post('/users/', status_code=status.HTTP_201_CREATED, tags=['users'])
def create_user(item: User):
    from api.users import create_user
    return create_user(item)



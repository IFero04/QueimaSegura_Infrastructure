import time
import nltk
from fastapi import FastAPI, status
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

from endpoints import auth, users, location, fires

app.include_router(auth.router, prefix="/auth", tags=['auth'])
app.include_router(users.router, prefix="/users", tags=['users'])
app.include_router(location.router, prefix="/location", tags=['location'])
app.include_router(fires.router, prefix="/fires", tags=['fires'])

## TEMP 
@app.get('/users/', status_code=status.HTTP_200_OK, tags=['users'])
def get_users():
    from api.users import get_users
    return get_users()

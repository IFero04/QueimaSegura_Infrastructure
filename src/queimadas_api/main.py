import time
import nltk
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from util.db import check_db
from util.config import settings

nltk.download('stopwords')

print("Loading DataBase ...")
while not check_db(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password):
    print("Retrying in 15 seconds ...")
    time.sleep(15)

print("DataBase loaded.")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=status.HTTP_200_OK, tags=['root'])
def read_root():
    return {"apiName": settings.app_name}

from endpoints import static, auth, admin, users, location, fires

app.include_router(auth.router, prefix="/auth", tags=['auth'])
app.include_router(admin.router, prefix="/admin", tags=['admin'])
app.include_router(users.router, prefix="/users", tags=['users'])
app.include_router(location.router, prefix="/location", tags=['location'])
app.include_router(fires.router, prefix="/fires", tags=['fires'])
app.include_router(static.router, prefix="/static", tags=['static'])

## TEMP 
@app.get('/users', status_code=status.HTTP_200_OK, tags=['root'])
def get_users():
    from api.temp import get_users
    return get_users()

@app.get('/fires', status_code=status.HTTP_200_OK, tags=['root'])
def get_fires():
    from api.temp import get_fires
    return get_fires()

@app.patch('/approve/fires', status_code=status.HTTP_200_OK, tags=['root'])
def approve_fires():
    from api.temp import approve_all_fires
    return approve_all_fires()
import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_authenticity import *
from util.check_strings import *


## USERS
def _check_new_user(user):
    check_full_name(user.fullName)
    check_email(user.email)
    check_password(user.password)
    check_nif(user.nif)
    check_type(user.type)

def create_user(admin_id ,session_id, user):
    try:
        check_admin_authenticity(admin_id, session_id)
        _check_new_user(user)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                INSERT INTO users(full_name, email, password, nif, type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            parameters = (user.fullName, user.email, user.password, user.nif, user.type, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('User not created')
            
            return {
                'status': 'OK!',
                'message': 'User created successfully!',
            }

    except Exception as e:
        errorMsg = str(e)
        if 'duplicate key value violates unique constraint' in errorMsg:
            if 'email' in errorMsg:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')
            if 'nif' in errorMsg:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='NIF already exists')
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errorMsg)
    
def _check_user_id(user_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = "SELECT id FROM users WHERE id = %s;"
        parameters = (user_id, )
        try:
            _ = db.execute_query(query, parameters, multi=False)
        except Exception as _:
            raise Exception('User not found')
    
def update_user(user_id, admin_id, session_id, user):
    try:
        check_admin_authenticity(admin_id, session_id)
        _check_user_id(user_id)
        queries_and_params = []
        if user.email:
            check_email(user.email)
            queries_and_params.append(("UPDATE users SET email = LOWER(%s) WHERE id = %s;", (user.email, user_id, )))
        if user.fullName:
            check_full_name(user.fullName)
            queries_and_params.append(("UPDATE users SET fullName = %s WHERE id = %s;", (user.fullName, user_id, )))
        if user.nif:
            check_nif(user.nif)
            queries_and_params.append(("UPDATE users SET nif = %s WHERE id = %s;", (user.nif, user_id, )))
        if user.type:
            check_type(user.type)
            queries_and_params.append(("UPDATE users SET type = %s WHERE id = %s;", (user.type, user_id,)))

        print(user)
        print(queries_and_params)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            for query, parameters in queries_and_params:
                db.execute_query(query, parameters, fetch=False)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
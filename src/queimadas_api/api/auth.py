import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_authenticity import *
from util.check_strings import *


## UTIL
def valid_email(email):
    try:
        check_email(email)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT email
                FROM users
                WHERE email = %s;
            """
            parameters = (email, )
            result = db.execute_query(query, parameters, multi=False)
            if result:
                raise Exception('Email already exists')

            return {
                'status': 'OK!',
                'message': 'Email is valid!'
            }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

## LOGIN
def _check_login(credentials):
    check_email(credentials.email)
    check_password(credentials.password)

def login(credentials):
    try:
        _check_login(credentials)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, full_name, nif, password, avatar, type, active, deleted
                FROM users
                WHERE email = %s;
            """
            parameters = (credentials.email, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:  
                raise Exception('User not found')
            user_id, full_name, nif, password, avatar, user_type, active, deleted = result
            if deleted:
                raise Exception('User not found')
            if not active:
                raise Exception('User Banned')
            if password != credentials.password:
                raise Exception('Invalid password')
            
            session = str(uuid.uuid4())

            query = """
                UPDATE users
                SET session_id = %s
                WHERE id = %s;
            """
            parameters = (session, user_id, )
            db.execute_query(query, parameters, fetch=False)

            return {
                'status': 'OK!',
                'message': 'User logged in successfully!',
                'result': {
                    'sessionId': session,
                    'user': {
                        'id': user_id,
                        'fullName': full_name,
                        'nif': int(nif),
                        'type': int(user_type),
                    }
                }
            }

    except Exception as e:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
## LOGOUT
def logout(user_id, session_id):
    try:
        check_session(user_id, session_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                UPDATE users
                SET session_id = NULL
                WHERE id = %s;
            """
            parameters = (user_id, )
            db.execute_query(query, parameters, fetch=False)

            return {
                'status': 'OK!',
                'message': 'User logged out successfully!'
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


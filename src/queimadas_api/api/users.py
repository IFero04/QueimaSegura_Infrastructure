import re
import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings

def get_users():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, session_id, full_name, email, nif, password, type
                FROM users
            """
            result = db.execute_query(query, fetch=True)
            if not result:
                raise Exception('No users found')
            
            users = []
            for user in result:
                users.append({
                    'user_id': user[0],
                    'session_id': user[1],
                    'full_name': user[2],
                    'email': user[3],
                    'nif': user[4],
                    'password': user[5],
                    'type': int(user[6])
                })

            return {
                'status': 'OK!',
                'message': 'Users found successfully!',
                'result': users
            }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

## GENERAL
def __check_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not(re.match(email_pattern, email)):
        raise Exception('Invalid email')

def __check_password(password):
    if len(password) != 32:
        raise Exception('Password must be a MD5 hash')

def __check_full_name(full_name):
    if len(full_name) < 3:
        raise Exception('Full name must have at least 3 characters')
    if not full_name.replace(" ", "").isalpha():
        raise Exception('Full name must have only letters')

def __check_nif(nif):
    if len(nif) != 9:
        raise Exception('NIF must have 9 digits')
    if not nif.isdigit():
        raise Exception('NIF must have only digits')
    if nif[0] in ('4','7'):
        raise Exception('Invalid NIF')

## REGISTER
def _check_new_user(user):
    __check_full_name(user.fullName)
    __check_email(user.email)
    __check_password(user.password)
    __check_nif(user.nif)

def create_user(user):
    try:
        _check_new_user(user)
        session = str(uuid.uuid4())

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                INSERT INTO users(full_name, email, password, nif, session_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            parameters = (user.fullName, user.email, user.password, user.nif, session, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('User not created')

            if user_id := result[0]:
                return {
                    'status': 'OK!',
                    'message': 'User created successfully!',
                    'result': {
                        'userId': user_id,
                        'sessionId': session
                    }
                }

    except Exception as e:
        errorMsg = str(e)
        print(' ERROR')
        print(e)
        print(' MSG')
        print(errorMsg)
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errorMsg)

## LOGIN
def _check_login(credentials):
    __check_email(credentials.email)
    __check_password(credentials.password)

def login(credentials):
    try:
        _check_login(credentials)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, full_name, nif, password, avatar, type
                FROM users
                WHERE email = %s
            """
            parameters = (credentials.email, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:  
                raise Exception('User not found')
            user_id, full_name, nif, password, avatar, user_type = result
            if password != credentials.password:
                raise Exception('Invalid password')
            
            session = str(uuid.uuid4())

            query = """
                UPDATE users
                SET session_id = %s
                WHERE id = %s
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
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT session_id
                FROM users
                WHERE id = %s
            """
            parameters = (user_id, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('User not found')

            if active_session := result[0]:
                if active_session != session_id:
                    raise Exception('Session_id does not match')
                
                query = """
                    UPDATE users
                    SET session_id = NULL
                    WHERE id = %s
                """
                parameters = (user_id, )
                db.execute_query(query, parameters, fetch=False)
    
                return {
                    'status': 'OK!',
                    'message': 'User logged out successfully!'
                }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

## UPDATE
def _check_update_user(user):
    __check_full_name(user.fullName)
    __check_email(user.email)
    __check_password(user.password)
    __check_nif(user.nif)

def update_user(user_id, session_id, user):
    try:
        _check_update_user(user)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT session_id
                FROM users
                WHERE id = %s
            """

            parameters = (user_id, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('User not found')
            
            if active_session := result[0]:
                if active_session != session_id:
                    raise Exception('Session_id does not match')
                
                query = """
                    UPDATE users
                    SET full_name = %s, email = %s, password = %s, nif = %s
                    WHERE id = %s
                """
                parameters = (user.fullName, user.email, user.password, user.nif, user_id, )
                db.execute_query(query, parameters, fetch=False)
    
                return {
                    'status': 'OK!',
                    'message': 'User updated successfully!'
                }
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
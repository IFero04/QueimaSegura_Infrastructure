import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_authenticity import *
from util.check_strings import *


## GET
def get_user(user_id, session_id):
    try:
        check_session(user_id, session_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, full_name, email, nif, type
                FROM users
                WHERE id = %s;
            """
            parameters = (user_id, )
            result = db.execute_query(query, parameters, fetch=True)
            if not result:
                raise Exception('User not found')
            
            user = {
                'id': result[0],
                'fullName': result[1],
                'email': result[2],
                'nif': result[3],
                'type': int(result[4])
            }

            return {
                'status': 'OK!',
                'message': 'User found successfully!',
                'result': user
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

## REGISTER
def _check_new_user(user):
    check_full_name(user.fullName)
    check_email(user.email)
    check_password(user.password)
    check_nif(user.nif)

def create_user(user):
    try:
        _check_new_user(user)
        session = str(uuid.uuid4())

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                INSERT INTO users(full_name, email, password, nif, session_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
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
        if 'duplicate key value violates unique constraint' in errorMsg:
            if 'email' in errorMsg:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')
            if 'nif' in errorMsg:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='NIF already exists')
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errorMsg)

## UPDATE
def update_user(user_id, session_id, user):
    try:
        check_session(user_id, session_id)
        queries_and_params = []
        if user.email:
            check_email(user.email)
            queries_and_params.append(("UPDATE users SET email = %s WHERE id = %s;", (user.email, user_id)))
        if user.fullName:
            check_full_name(user.fullName)
            queries_and_params.append(("UPDATE users SET full_name = %s WHERE id = %s;", (user.fullName, user_id)))
        if user.nif:
            check_nif(user.nif)
            queries_and_params.append(("UPDATE users SET nif = %s WHERE id = %s;", (user.nif, user_id)))

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            for query, parameters in queries_and_params:
                db.execute_query(query, parameters, fetch=False)
    
        return {
            'status': 'OK!',
            'message': 'User updated successfully!'
        }
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

## STATUS
def __check_permissions(fire_id):
    query = """
        SELECT icnf_permited, gestor_permited
        FROM permissions
        WHERE fire_id = %s
    """
    parameters = (fire_id, )
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        permissions = db.execute_query(query, parameters)
    if not permissions:
        return True
    icnf_permited, gestor_permited = permissions[0]
    return icnf_permited and gestor_permited

def get_user_status(user_id, session_id):
    try:
        check_session(user_id, session_id)
        
        query = """
            SELECT id, status
            FROM fires
            WHERE user_id = %s AND cancelled = FALSE;
        """
        parameters = (user_id, )
        
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            result = db.execute_query(query, parameters)
        
            user_fires_complete = 0
            user_fires_pending = 0
            
            if result:
                for fire_id, fire_status in result:
                    query = """
                        SELECT icnf_permited, gestor_permited
                        FROM permissions
                        WHERE fire_id = %s;
                    """
                    parameters = (fire_id, )
                    perm_result = db.execute_query(query, parameters)
                    if fire_status == "Scheduled":
                        if perm_result:
                            user_fires_pending += 1
                    elif fire_status == "Completed":
                        if perm_result and perm_result[0] and  perm_result[1]:
                            user_fires_complete += 1
                        else:
                            user_fires_complete += 1

        return {
            'status': 'OK!',
            'message': 'User status found successfully!',
            'result': {
                'firesComplete': user_fires_complete,
                'firesPending': user_fires_pending
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
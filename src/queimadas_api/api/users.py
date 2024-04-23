import re
import uuid
from util.db import PostgresDB
from const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD


#GENERAL
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
    expected_keys = {'full_name', 'email', 'password', 'NIF'}
    keys = user.keys()
    missing_keys = expected_keys - set(user.keys())

    if keys != expected_keys:
        raise Exception('Invalid keys')
    if missing_keys:
        raise Exception(f'Missing keys: {missing_keys}')
    
    __check_full_name(user['full_name'])
    __check_email(user['email'])
    __check_password(user['password'])
    __check_nif(user['NIF'])

def new_user(data):
    try:
        user = data['user']
        _check_new_user(user)
        session = str(uuid.uuid4())

        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query = """
                INSERT INTO users(full_name, email, password, nif, session_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            parameters = (user['full_name'], user['email'], user['password'], user['NIF'], session)
            result = db.execute_query(query, parameters)

            if user_id := result[0]:
                return {
                    'status': 'OK!',
                    'message': 'User created successfully!',
                    'result': {
                        'user_id': user_id,
                        'session_id': session
                    }
                }, 201
            
            raise Exception('User not created')
    except Exception as e:
        return {
            'status': 'ERROR!',
            'message': str(e)
        }, 400

## LOGIN
def _check_login(login):
    expected_keys = {'email', 'password'}
    keys = login.keys()
    missing_keys = expected_keys - set(login.keys())

    if keys != expected_keys:
        raise Exception('Invalid keys')
    if missing_keys:
        raise Exception(f'Missing keys: {missing_keys}')

    __check_email(login['email'])
    __check_password(login['password'])

def login(data):
    try:
        login = data['login']
        _check_login(login)
        session = str(uuid.uuid4())

        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query = """
                SELECT id
                FROM users
                WHERE email = %s AND password = %s
            """
            parameters = (login['email'], login['password'])
            result = db.execute_query(query, parameters)

            if user_id := result[0]:
                query = """
                    UPDATE users
                    SET session_id = %s
                    WHERE id = %s
                """
                parameters = (session, user_id)
                db.execute_query(query, parameters, fetch=False)

                return {
                    'status': 'OK!',
                    'message': 'User logged in successfully!',
                    'result': {
                        'user_id': user_id,
                        'session_id': session
                    }
                }, 200
            
            raise Exception('User not found')

    except Exception as e:
        return {
            'status': 'ERROR!',
            'message': str(e)
        }, 400

## LOGOUT
def logout(args):
    try:
        user_id = args['id']
        session_id = args['session_id']

        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query = """
                SELECT session_id
                FROM users
                WHERE id = %s
            """
            parameters = (user_id)
            result = db.execute_query(query, parameters)

            if active_session := result[0]:
                if active_session != session_id:
                    raise Exception('Session_id does not match')
                
                query = """
                    UPDATE users
                    SET session_id = NULL
                    WHERE id = %s
                """
                parameters = (user_id)
                db.execute_query(query, parameters, fetch=False)
    
                return {
                    'status': 'OK!',
                    'message': 'User logged out successfully!'
                }, 200
            
            raise Exception('User not found')

    except Exception as e:
        return {
            'status': 'ERROR!',
            'message': str(e)
        }, 400

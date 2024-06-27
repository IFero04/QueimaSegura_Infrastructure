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

def get_admin_status(admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        fires_to_aprrove = 0

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT COUNT(p.id)
                FROM permissions p
                JOIN fires f ON p.fire_id = f.id
                WHERE p.gestor_user_id IS NULL AND f.status = 'Scheduled' and f.cancelled = false;
            """
            result = db.execute_query(query)
            fires_to_aprrove = result
            query = """
                SELECT COUNT(p.id)
                FROM permissions p
                JOIN fires f ON p.fire_id = f.id
                WHERE gestor_user_id = %s ADN f.status != 'Scheduled' and f.cancelled = false;
            """
            parameters = (admin_id, )
            result = db.execute_query(query, parameters)
            fires_approved = result

        return {
            'status': 'OK!',
            'message': 'Admin status found successfully!',
            'result': {
                'firesApproved': fires_approved,
                'firesWaiting': fires_to_aprrove
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
def get_users(admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, full_name, email, nif, type, active
                FROM users
                WHERE deleted = false
            """
            result = db.execute_query(query, fetch=True)
            if not result:
                raise Exception('No users found')
            
            users = []
            for user in result:
                users.append({
                    'user_id': user[0],
                    'full_name': user[1],
                    'email': user[2],
                    'nif': user[3],
                    'type': int(user[4]),
                    'active': user[5]
                })

            return {
                'status': 'OK!',
                'message': 'Users found successfully!',
                'result': users
            }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

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
    
def update_user(user_id, admin_id, session_id, user):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)
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
        if user.type:
            check_type(user.type)
            queries_and_params.append(("UPDATE users SET type = %s WHERE id = %s;", (user.type, user_id)))

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            for query, parameters in queries_and_params:
                db.execute_query(query, parameters, fetch=False)
        
        return {
            'status': 'OK!',
            'message': 'User updated successfully!'
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
def delete_user(user_id, admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = "Update users SET deleted = true WHERE id = %s;"
            parameters = (user_id, )
            db.execute_query(query, parameters, fetch=False)
        
        return {
            'status': 'OK!',
            'message': 'User deleted'
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def ban_user(user_id, admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = "Update users SET active = false WHERE id = %s;"
            parameters = (user_id, )
            db.execute_query(query, parameters, fetch=False)
        
        return {
            'status': 'OK!',
            'message': 'User banned'
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def unban_user(user_id, admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = "Update users SET active = true WHERE id = %s;"
            parameters = (user_id, )
            db.execute_query(query, parameters, fetch=False)
        
        return {
            'status': 'OK!',
            'message': 'User unbanned'
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

                            
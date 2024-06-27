from datetime import datetime
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
            result = db.execute_query(query, multi=False)
            fires_to_aprrove = result
            query = """
                SELECT COUNT(p.id)
                FROM permissions p
                JOIN fires f ON p.fire_id = f.id
                WHERE p.gestor_user_id = %s AND f.status != 'Scheduled' and f.cancelled = false;
            """
            parameters = (admin_id, )
            result = db.execute_query(query, parameters, multi=False)
            fires_approved = result

        return {
            'status': 'OK!',
            'message': 'Admin status found successfully!',
            'result': {
                'firesApproved': fires_approved[0],
                'firesWaiting': fires_to_aprrove[0]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
def get_users(admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, full_name, email, type, active, deleted
                FROM users
                WHERE type != 2;
            """
            result = db.execute_query(query, fetch=True)
            
            users = []
            for user in result:
                user_id, name, email, user_type, active, deleted = user
                users.append({
                    'userId': user_id,
                    'fullName': name,
                    'email': email,
                    'type': int(user_type),
                    'active': active,
                    'deleted': deleted
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
    
def update_user_perms(user_id, perm, admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            querry = """
                UPDATE users SET type = %s WHERE id = %s
            """
            parameters = (perm, user_id)
            db.execute_query(querry, parameters, fetch=False)
        
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
            query = "Update users SET deleted = true AND active = true WHERE id = %s;"
            parameters = (user_id, )
            db.execute_query(query, parameters, fetch=False)
        
        return {
            'status': 'OK!',
            'message': 'User deleted'
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def restore_user(user_id, admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = "Update users SET deleted = false AND active = true WHERE id = %s;"
            parameters = (user_id, )
            db.execute_query(query, parameters, fetch=False)
        
        return {
            'status': 'OK!',
            'message': 'User restored'
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
    
def search_user(search, admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, full_name, email, nif, deleted
                FROM users
                WHERE full_name ILIKE %s OR email ILIKE %s OR nif ILIKE %s AND type != 2;
            """
            parameters = (f'%{search}%', f'%{search}%', f'%{search}%', )
            result = db.execute_query(query, parameters)
            
            users = []
            for user in result:
                user_id, name, email, nif, deleted = user
                if deleted:
                    continue
                users.append({
                    'userId': user_id,
                    'fullName': name,
                    'email': email,
                    'nif': nif
                })

            return {
                'status': 'OK!',
                'message': 'Users found successfully!',
                'result': users
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def get_request_to_approve(admin_id, session_id):
    try:
        check_admin_authenticity(admin_id, session_id)
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT p.id, f.id, f.date, r.name_pt, r.name_en, c.name
                FROM permissions p
                JOIN fires f ON p.fire_id = f.id
                JOIN reasons r ON f.reason_id = r.id
                JOIN zip_codes z ON f.zip_code_id = z.id
                JOIN counties c ON z.county_id = c.id
                WHERE p.gestor_user_id IS NULL AND f.status = 'Scheduled' and f.cancelled = false;
            """
            result = db.execute_query(query, fetch=True)
            
            requests = []
            for request in result:
                perm_id, fire_id, date, reason_pt, reason_en, county= request
                requests.append({
                    'permId': perm_id,
                    'fire': {
                        'id': fire_id,
                        'date': date,
                        'county': county
                    },
                    'reason': {
                        'namePt': reason_pt,
                        'nameEn': reason_en
                    }
                })

            return {
                'status': 'OK!',
                'message': 'Requests found successfully!',
                'result': requests
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
                            
def __check_fire_date(fire_date_str):
    fire_date = datetime.strptime(fire_date_str, '%m/%d/%Y').date()
    today = datetime.today().date()
    if fire_date <= today:
        raise Exception('Date must be greater than today')

## REGISTER
def __check_new_fire(user_id, fire):
    check_type_id(fire.typeId)
    check_reason_id(fire.reasonId)
    check_zip_code_id(fire.zipCodeId)
    check_fire_approved(fire.zipCodeId, fire.date)
    check_existing_fire(user_id, fire.zipCodeId, fire.date)
    __check_fire_date(fire.date)

def create_fire(admin_id, session_id, user_id, fire):
    try:
        check_admin_authenticity(admin_id, session_id)
        check_user_id(user_id)
        __check_new_fire(user_id, fire)
    
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                INSERT INTO fires (date, type_id, reason_id, zip_code_id, user_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """

            parameters = (fire.date, fire.typeId, fire.reasonId, fire.zipCodeId, user_id)
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('Fire not created')
            
            fire_id = result[0]

            if fire.location:
                query = """
                    UPDATE fires
                    SET location = %s
                    WHERE id = %s
                """
                parameters = (fire.location, fire_id)
                db.execute_query(query, parameters, fetch=False)
            
            if fire.observations:
                query = """
                    UPDATE fires
                    SET observations = %s
                    WHERE id = %s
                """
                parameters = (fire.observations, fire_id)
                db.execute_query(query, parameters, fetch=False)

            query = """
                SELECT id, name_pt
                FROM types
                WHERE id = %s
            """
            parameters = (fire.typeId,)
            result = db.execute_query(query, parameters, multi=False)
            fire_type = result[1]
            if fire_type == 'Queimada':
                query = """
                    INSERT INTO permissions (fire_id)
                    VALUES (%s)
                """
                parameters = (fire_id,)
                db.execute_query(query, parameters, fetch=False)

            return {
                'status': 'OK!',
                'message': 'Fire created successfully!',
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

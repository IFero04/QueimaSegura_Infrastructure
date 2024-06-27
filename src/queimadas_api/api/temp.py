import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_authenticity import *
from util.check_strings import *


def get_users():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, session_id, full_name, email, nif, password, type, active, deleted
                FROM users;
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
                    'type': int(user[6]),
                    'active': user[7],
                    'deleted': user[8]
                })

        return {
            'status': 'OK!',
            'message': 'Users found successfully!',
            'result': users
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
def get_fires():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT 
                    f.id, 
                    f.date,
                    f.status, 
                    t.name_en AS type, 
                    r.name_en AS reason, 
                    z.zip_code, 
                    f.location, 
                    f.observations
                FROM 
                    fires f
                JOIN 
                    types t ON f.type_id = t.id
                JOIN 
                    reasons r ON f.reason_id = r.id
                JOIN 
                    zip_codes z ON f.zip_code_id = z.id
            """

            result = db.execute_query(query)
            if not result:
                raise Exception('No fires found')

            fires = []
            for fire in result:
                fire_id, date, status, type, reason, zip_code, location, observations = fire
                fires.append({
                    'fireId': fire_id,
                    'date': date,
                    'status': status,
                    'type': type,
                    'reason': reason,
                    'zipCode': zip_code,
                    'location': location,
                    'observations': observations
                })

            return {
                'status': 'OK!',
                'message': 'Fires found successfully!',
                'result': fires
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
def approve_all_fires():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                Update permissions
                SET icnf_permited = TRUE, gestor_permited = TRUE
            """
            db.execute_query(query, fetch=False)

        return {
            'status': 'OK!',
            'message': 'All fires approved successfully!'
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
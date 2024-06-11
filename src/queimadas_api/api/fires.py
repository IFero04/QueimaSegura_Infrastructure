from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings

## GENERAL    
def __check_user(user_id, session_id):
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

def __check_type_id(type_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id
                FROM types
                WHERE id = %s
            """

            parameters = (type_id, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('Type not found')

def __check_reason_id(reason_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id
                FROM reasons
                WHERE id = %s
            """

            parameters = (reason_id, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('Reason not found')

def __check_zip_code_id(zip_code_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id
                FROM zip_codes
                WHERE id = %s
            """

            parameters = (zip_code_id, )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('Zip Code not found')
    

## REGISTER
def __check_new_fire(fire):
    __check_type_id(fire.typeId)
    __check_reason_id(fire.reasonId)
    __check_zip_code_id(fire.zipCodeId)

def create_fire(user_id, session_id, fire):
    try:
        __check_user(user_id, session_id)
        __check_new_fire(fire)
    
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
            
            if fire_id := result[0]:
                if fire.location:
                    query = f"""
                        UPDATE fires(location)
                        VALUES (%s)
                        WHERE id = {fire_id}
                    """
                    parameters = (fire.location)
                    db.execute_query(query, parameters, fetch=False)
                if fire.observations:
                    query = f"""
                        UPDATE fires(observations)
                        VALUES (%s)
                        WHERE id = {fire_id}
                    """
                    parameters = (fire.observations)
                    db.execute_query(query, parameters, fetch=False)
                return {
                    'status': 'OK!',
                    'message': 'Fire created successfully!',
                    'result': {
                        'fireId': fire_id
                    }
                }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))






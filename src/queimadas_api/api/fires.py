from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_authenticity import *
from util.check_strings import *
  

## REGISTER
def __check_new_fire(fire):
    check_type_id(fire.typeId)
    check_reason_id(fire.reasonId)
    check_zip_code_id(fire.zipCodeId)
    check_fire_approved(fire.zipCodeId, fire.date)

def create_fire(user_id, session_id, fire):
    try:
        check_session(user_id, session_id)
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
                'result': {
                    'fireId': fire_id
                }
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


## GET
def get_user_fires(user_id, session_id):
    try:
        check_session(user_id, session_id)
    
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT 
                    f.id, 
                    f.date, 
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
                WHERE 
                    f.user_id = %s
            """

            parameters = (user_id,)
            result = db.execute_query(query, parameters)
            if not result:
                raise Exception('No fires found')

            fires = []
            for fire in result:
                fire_id, date, type, reason, zip_code, location, observations = fire
                fires.append({
                    'fireId': fire_id,
                    'date': date,
                    'type': type,
                    'reason': reason,
                    'zipCode': zip_code,
                    'location': location,
                    'observations': observations
                })

            return {
                'status': 'OK!',
                'message': 'Fires found!',
                'result': fires
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))





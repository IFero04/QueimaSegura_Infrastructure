from datetime import datetime
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_authenticity import *
from util.check_strings import *

  
def __check_fire_date(fire_date_str):
    fire_date = datetime.strptime(fire_date_str, '%m/%d/%Y').date()
    today = datetime.today().date()
    if fire_date < today:
        raise Exception('Date must be greater than today')

## REGISTER
def __check_new_fire(user_id, fire):
    check_type_id(fire.typeId)
    check_reason_id(fire.reasonId)
    check_zip_code_id(fire.zipCodeId)
    check_fire_approved(fire.zipCodeId, fire.date)
    check_existing_fire(user_id, fire.zipCodeId, fire.date)
    __check_fire_date(fire.date)

def create_fire(user_id, session_id, fire):
    try:
        check_session(user_id, session_id)
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
            
            query = """
                SELECT 
                    f.date,
                    f.status,
                    t.name_en,
                    t.name_pt
                FROM 
                    fires f
                JOIN 
                    types t ON f.type_id = t.id
                WHERE 
                    f.user_id = %s AND f.id = %s AND f.cancelled = FALSE
            """

            parameters = (user_id, fire_id)
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('Error fetching fire details')

            date, fire_status, type_en, type_pt = result

            return {
                'status': 'OK!',
                'message': 'Fire created successfully!',
                'result': {
                    'fireId': fire_id,
                    'date': date,
                    'status': fire_status,
                    'typeEn': type_en,
                    'typePt': type_pt
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
                    f.status,
                    t.name_en,
                    t.name_pt
                FROM 
                    fires f
                JOIN 
                    types t ON f.type_id = t.id
                WHERE 
                    f.user_id = %s AND f.cancelled = FALSE
            """

            parameters = (user_id,)
            result = db.execute_query(query, parameters)

            fires = []
            for fire in result:
                fire_id, date, fire_status, type_en, type_pt = fire
                query = """
                    SELECT icnf_permited, gestor_permited
                    FROM permissions
                    WHERE fire_id = %s;
                """
                parameters = (fire_id,)
                permissions = db.execute_query(query, parameters, multi=False)

                if fire_status == 'Scheduled' and permissions:
                    icnf_permitted, gestor_permitted = permissions
                    if icnf_permitted and gestor_permitted:
                        transformed_status = 'Approved'
                    else:
                        transformed_status = 'Pending'
                else:
                    transformed_status = fire_status
                
                if fire_status == 'Ongoing' and permissions:
                    icnf_permitted, gestor_permitted = permissions
                    if not icnf_permitted or not gestor_permitted:
                        transformed_status = 'Not Aprroved'

                if fire_status == 'Completed' and permissions:
                    icnf_permitted, gestor_permitted = permissions
                    if not icnf_permitted or not gestor_permitted:
                        transformed_status = 'Not Approved'

                fires.append({
                    'id': fire_id,
                    'date': date,
                    'status': transformed_status,
                    'typeEn': type_en,
                    'typePt': type_pt
                })

            return {
                'status': 'OK!',
                'message': 'Fires found!',
                'result': fires
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def get_fire_detail(user_id, session_id, fire_id):
    try:
        check_session(user_id, session_id)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT
                    f.cancelled, 
                    f.id, 
                    f.date,
                    f.status,
                    f.location,
                    f.observations,
                    t.name_en,
                    t.name_pt,
                    r.name_en,
                    r.name_pt,
                    z.zip_code,
                    z.location_name,
                    z.ART_name,
                    z.tronco
                FROM 
                    fires f
                JOIN 
                    types t ON f.type_id = t.id
                JOIN 
                    reasons r ON f.reason_id = r.id
                JOIN 
                    zip_codes z ON f.zip_code_id = z.id
                WHERE 
                    f.id = %s
            """

            parameters = (fire_id,)
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('Fire not found')

            cancelled, fire_id, date, fire_status, location, observations, type_en, type_pt, reason_en, reason_pt, zip_code, location_name, ART_name, tronco = result
            if cancelled:
                raise Exception('Fire cancelled')
            return {
                'status': 'OK!',
                'message': 'Fire found!',
                'result': {
                    'fire': {
                        'id': fire_id,
                        'date': date,
                        'status': fire_status,
                        'latlng': location,
                        'observations': observations,
                    },
                    'type': {
                        'namePt': type_pt,
                        'nameEn': type_en
                    },
                    'reason': {
                        'reasonEn': reason_en,
                        'reasonPt': reason_pt
                    },
                    'zipCode': {
                        'id': zip_code,
                        'zipCode': zip_code,
                        'locationName': location_name,
                        'artName': ART_name,
                        'tronco': tronco
                    }
                }
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 

## CANCEL
def delete_fire(user_id, session_id, fire_id):
    try:
        check_session(user_id, session_id)

        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                UPDATE fires
                SET cancelled = TRUE
                WHERE id = %s
            """

            parameters = (fire_id,)
            db.execute_query(query, parameters, fetch=False)

            return {
                'status': 'OK!',
                'message': 'Fire cancelled successfully!'
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


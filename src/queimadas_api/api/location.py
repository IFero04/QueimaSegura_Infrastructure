import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings


## ZIPCODE
def get_location(zipcode):
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, location_code, location_name, ART_code, ART_name, tronco, client, zip_code, zip_name, county_id
                FROM zip_codes
                WHERE zip_code LIKE %s;
            """
            parameters = (zipcode, )
            result = db.execute_query(query, parameters, multi=True)
            if not result:
                raise HTTPException(status_code=404, detail='Location not found')
            result_json = []
            for r in result:
                id, location_code, location_name, ART_code, ART_name, tronco, client, zip_code, zip_name, county_id = r
                result_json.append({
                    'id': id,
                    'location_code': location_code,
                    'location_name': location_name,
                    'ART_code': ART_code,
                    'ART_name': ART_name,
                    'tronco': tronco,
                    'client': client,
                    'zip_code': zip_code,
                    'zip_name': zip_name,
                    'county_id': county_id
                })
                
            return {
                    'status': 'OK!',
                    'message': 'User created successfully!',
                    'result': result_json
                }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
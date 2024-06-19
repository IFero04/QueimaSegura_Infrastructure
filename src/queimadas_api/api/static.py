import uuid
from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings
from util.check_strings import *


def get_types():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, name_pt, name_en
                FROM types;
            """
            result = db.execute_query(query, multi=True)

            types = []
            for type in result:
                types.append({
                    'id': type[0],
                    'namePt': type[1],
                    'nameEn': type[2]
                })
            
            return {
                'status': 'OK!',
                'message': 'Types found successfully!',
                'result': types
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def get_reasons():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, name_pt, name_en
                FROM reasons;
            """
            result = db.execute_query(query, multi=True)

            reasons = []
            for reason in result:
                reasons.append({
                    'id': reason[0],
                    'namePt': reason[1],
                    'nameEn': reason[2]
                })
            
            return {
                'status': 'OK!',
                'message': 'Reasons found successfully!',
                'result': reasons
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def get_controller():
    try:
        with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT id, name
                FROM controller
                ORDER BY id DESC
                LIMIT 1;
            """
            result = db.execute_query(query, multi=False)

            return {
                'status': 'OK!',
                'message': 'Controllers found successfully!',
                'result': {
                    'id': result[0],
                    'name': result[1]
                }
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
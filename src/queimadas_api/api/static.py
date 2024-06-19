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
                    'name_pt': type[1],
                    'name_en': type[2]
                })
            
            return {
                'status': 'OK!',
                'message': 'Types found successfully!',
                'result': types
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
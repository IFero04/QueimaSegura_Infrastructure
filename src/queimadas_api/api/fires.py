from fastapi import HTTPException, status
from util.db import PostgresDB
from util.config import settings

## GENERAL    
def __check_user(user):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
            query = """
                SELECT session_id
                FROM users
                WHERE id = %s
            """

            parameters = (user['user_id'], )
            result = db.execute_query(query, parameters, multi=False)
            if not result:
                raise Exception('User not found')
            
            if active_session := result[0]:
                if active_session != user['session_id']:
                    raise Exception('Session_id does not match')



## REGISTER
def _check_new_fire(fire):
    pass

def new_fire(data):
    user = data['user']
    fire = data['fire']
    __check_user(user)
    _check_new_fire(fire)





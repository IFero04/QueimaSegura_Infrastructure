from util.db import PostgresDB
from queimadas_api.util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD

## GENERAL
def __check_keys(expected_keys, keys):
    missing_keys = expected_keys - set(keys)
    if keys != expected_keys:
        raise Exception('Invalid keys')
    if missing_keys:
        raise Exception(f'Missing keys: {missing_keys}')
    
def __check_user(user):
    expected_keys = {'user_id', 'session_id'}
    __check_keys(expected_keys, user.keys())

    with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
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
    expected_keys = {'type', 'date', 'location', 'reason', 'county'}
    __check_keys(expected_keys, fire.keys())

def new_fire(data):
    user = data['user']
    fire = data['fire']
    __check_user(user)
    _check_new_fire(fire)





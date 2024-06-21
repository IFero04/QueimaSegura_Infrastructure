from util.db import PostgresDB
from util.config import settings

def check_user_id(user_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = """
            SELECT id
            FROM users
            WHERE id = %s;
        """
        parameters = (user_id, )
        try:
            result = db.execute_query(query, parameters, multi=False)
        except Exception as _:
            raise Exception('User not found')
        
        if not result:
            raise Exception('User not found')

def check_session(user_id, session_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = """
            SELECT session_id
            FROM users
            WHERE id = %s;
        """
        parameters = (user_id, )
        try:
            result = db.execute_query(query, parameters, multi=False)
        except Exception as _:
            raise ('User not found')
        
        if active_session := result[0]:
            if active_session != session_id:
                raise Exception('Session does not match')
        else:
            raise Exception('Session does not exist')

def check_admin_authenticity(admin_id, session_id):
    with PostgresDB(settings.pg_host, settings.pg_port, settings.pg_db_name, settings.pg_user, settings.pg_password) as db:
        query = """
            SELECT session_id, type
            FROM users
            WHERE id = %s;
        """
        parameters = (admin_id, )
        try:
            result = db.execute_query(query, parameters, multi=False)
        except Exception as _:
            raise Exception('User not found')
        
        if active_session := result[0]:
            if active_session != session_id:
                raise Exception('Session does not match')
        else:
            raise Exception('Session does not exist')
        
        if type := result[1]:
            if type != 2:
                raise Exception('User is not an admin')

def check_zip_code_id(zip_code_id):
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
            
def check_reason_id(reason_id):
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

def check_type_id(type_id):
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
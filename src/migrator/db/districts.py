from util.db import PostgresDB
from util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD


def migrate_districts():
    districts = {}
    with open('/data/distritos.txt', 'r', encoding='utf-8', errors='replace') as file:
        for line in file:
            cod, name = line.strip().split(';')
            districts[cod] = name
    try:
        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query_check = """
                SELECT id FROM districts WHERE name = %s
            """
            query_insert = """
                INSERT INTO districts(id, name) VALUES (%s, %s) RETURNING id
            """
            for cod, name in districts.items():
                cod_int = int(cod)
                parameters_check = (name, )
                existing_district = db.execute_query(query_check, parameters_check, multi=False)
                if existing_district:
                    continue
                parameters_insert = (cod_int, name)
                result = db.execute_query(query_insert, parameters_insert, multi=False)
                if not result:
                    raise Exception('District not created')
                if cod_int != result[0]:
                    raise Exception('District created with different id')
                
        print('Districts migrated successfully!')
        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


            
       
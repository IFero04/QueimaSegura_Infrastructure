from util.db import PostgresDB
from util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD


def migrate_counties():
    counties = []
    try:
        with open('/data/concelhos.txt', 'r', encoding='utf-8', errors='replace') as file:
            for line in file:
                split_line = line.strip().split(';')
                district_code = int(split_line[0])
                code = int(split_line[1])
                name = split_line[2]
                counties.append({"code": code, "name": name, "fk": district_code})
    except Exception as e:
        print(f"An error occurred during extraction: {str(e)}")
        return False

    try:
        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query_check = """
                SELECT id FROM counties WHERE name = %s
            """
            query_insert = """
                INSERT INTO counties(code, name, district_id) VALUES (%s, %s, %s) RETURNING id
            """
            for county in counties:
                parameters_check = (county["name"], )
                existing_county = db.execute_query(query_check, parameters_check, multi=False)
                if existing_county:
                    continue
                parameters_insert = (county["code"], county["name"], county["fk"], )
                result = db.execute_query(query_insert, parameters_insert, multi=False)
                if not result:
                    raise Exception('County not created')

        print('Counties migrated successfully!')
        return True
    except Exception as e:
        print(f"An error occurred during migration: {str(e)}")
        return False
from util.db import PostgresDB
from util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD


def __get_ART_name(ART_info, ART_local):
    non_empty_ART_info = [info for info in ART_info if info != ""]
    if not non_empty_ART_info and not ART_local:
        return None
    
    if not ART_local:
        return " ".join(non_empty_ART_info) 
    
    return " ".join(non_empty_ART_info) + " - " + ART_local

def __get_client(client_code, client_name):
    if not client_code and not client_name:
        return None
    if not client_code:
        return client_name
    return f"{client_code}: {client_name}"

def migrate_zipcode():
    zipcodes = []
    try:
        with open('/data/todos_cp.txt', 'r', encoding='utf-8', errors='replace') as file:
            for line in file:
                split_line = line.strip().split(';')
                DD, CC, location_code, location_name, ART_code, *ART_info, ART_local, tronco, client_code, client_name, CP4, CP3, zip_name = split_line
                
                ART_name = __get_ART_name(ART_info, ART_local)
                client = __get_client(client_code, client_name)
                zip_code = f"{CP4}-{CP3}"
                zipcodes.append({
                    "DD": int(DD),
                    "CC": int(CC),
                    "location_code": int(location_code),
                    "location_name": location_name,
                    "ART_code": int(ART_code) if ART_code else None,
                    "ART_name": ART_name,
                    "tronco": tronco if tronco else None,
                    "client": client,
                    "zip_code": zip_code,
                    "zip_name": zip_name
                })
    except Exception as e:
        print(f"An error occurred during extraction: {str(e)}")
        return False

    try:
        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query_check = """
                SELECT id FROM zip_codes WHERE zip_code = %s
            """
            query_get_fk = """
                SELECT id FROM counties WHERE code = %s AND district_id = %s
            """
            query_insert = """
                INSERT INTO zip_codes(
                    location_code,
                    location_name,
                    ART_code,
                    ART_name,
                    tronco,
                    client,
                    zip_code,
                    zip_name,
                    county_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """
            size = len(zipcodes)
            for i, zipcode in enumerate(zipcodes):
                print(f"[{i}/{size}] - {zipcode}")
                parameters_check = (zipcode["zip_code"], )
                existing_zipcode = db.execute_query(query_check, parameters_check, multi=False)
                if existing_zipcode:
                    continue
                parameters_get_fk = (zipcode["CC"], zipcode["DD"], )
                fk = db.execute_query(query_get_fk, parameters_get_fk, multi=False)
                if not fk:
                    raise Exception(f"County not found for zipcode: {zipcode['zip_code']}")
                parameters_insert = (
                    zipcode["location_code"],
                    zipcode["location_name"],
                    zipcode["ART_code"],
                    zipcode["ART_name"],
                    zipcode["tronco"],
                    zipcode["client"],
                    zipcode["zip_code"],
                    zipcode["zip_name"],
                    fk,
                )
                result = db.execute_query(query_insert, parameters_insert, multi=False)
                if not result:
                    raise Exception('ZIPCODE not created')
                    
                    
        print('Zipcodes migrated successfully!')
        return True
    except Exception as e:
        print(f"An error occurred during migration: {str(e)}")
        return False
    
def check_zipcodes():
    try:
        with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
            query = """
                SELECT COUNT(id) FROM zip_codes
            """
            result = db.execute_query(query, parameters=None, multi=False)
            print(result)
    except Exception as e:
        print(f"An error occurred during migration: {str(e)}")
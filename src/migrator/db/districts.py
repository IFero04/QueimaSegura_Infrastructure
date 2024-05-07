from util.db import PostgresDB
from util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD


def migrate_districts():
    districts = {}
    with open('/data/distritos.txt', 'r', encoding='utf-8', errors='replace') as file:
        for line in file:
            cod, name = line.strip().split(';')
            districts[cod] = name
    print(districts)

            
       
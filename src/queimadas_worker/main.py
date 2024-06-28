import time
from util.db import check_db, PostgresDB
from util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD

def main():
    with PostgresDB(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD) as db:
        query = """
            UPDATE public.fires
            SET date = date
        """
        db.execute_query(query, fetch=False)

if __name__ == '__main__':
    print("Loading DataBase ...")
    while not check_db(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD):
        print("Retrying in 15 seconds ...")
        time.sleep(15)

    print("DataBase loaded.")
    main()

import time
from util.db import check_db
from util.const import PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD
from db.districts import migrate_districts


def main():
    migrate_districts()
    

if __name__ == '__main__':
    print("Loading DataBase ...")
    while not check_db(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD):
        print("Retrying in 15 seconds ...")
        time.sleep(15)

    print("DataBase loaded.")
    main()
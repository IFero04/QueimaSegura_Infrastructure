import sys

# Constants
PG_HOST = str(sys.argv[1]) if len(sys.argv) >= 2 else None
PG_PORT = int(sys.argv[2]) if len(sys.argv) >= 3 else None
PG_DB_NAME = str(sys.argv[3]) if len(sys.argv) >= 4 else None
PG_USER = str(sys.argv[4]) if len(sys.argv) >= 5 else None
PG_PASSWORD = str(sys.argv[5]) if len(sys.argv) >= 6 else None

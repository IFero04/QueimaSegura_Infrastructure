#!/bin/bash

while true; do
  python -u main.py $PG_HOST $PG_PORT $PG_DB_NAME $PG_ADMIN_USER $PG_ADMIN_PASSWORD;

  echo "Executed worker at $(date)"
  echo "Sleeping for 3 hours"
  sleep 10800
done


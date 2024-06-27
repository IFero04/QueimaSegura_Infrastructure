#!/bin/bash

while true; do
  if [ "$USE_DEV_MODE" = "true" ];
    then nodemon --legacy-watch --exec python -u main.py $PG_HOST $PG_PORT $PG_DB_NAME $PG_ADMIN_USER $PG_ADMIN_PASSWORD; 
    else python -u main.py $PG_HOST $PG_PORT $PG_DB_NAME $PG_ADMIN_USER $PG_ADMIN_PASSWORD;
  fi

  echo "Executed worker at $(date)"
  echo "Sleeping for 3 hours"
  sleep 10800
done


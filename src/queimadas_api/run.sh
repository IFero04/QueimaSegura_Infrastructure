#!/bin/bash
if [ "/" = "true" ];
    then nodemon --legacy-watch --exec python -u main.py $API_PORT $PG_HOST $PG_PORT $PG_DB_NAME $PG_USER $PG_PASSWORD; 
    else python -u main.py $API_PORT $PG_HOST $PG_PORT $PG_DB_NAME $PG_USER $PG_PASSWORD;
fi

echo "Executed script at $(date)"

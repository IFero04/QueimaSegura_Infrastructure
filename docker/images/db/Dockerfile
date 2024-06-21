FROM postgres

ENV POSTGRES_PASSWORD=top_secret

COPY schema.sql /docker-entrypoint-initdb.d/

EXPOSE $DB_PORT
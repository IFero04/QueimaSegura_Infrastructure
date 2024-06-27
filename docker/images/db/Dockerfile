FROM postgres:14

ENV POSTGRES_PASSWORD=top_secret

RUN apt-get update && \
    apt-get install -y postgresql-14-cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo "shared_preload_libraries = 'pg_cron'" >> /usr/share/postgresql/postgresql.conf.sample

COPY schema.sql /docker-entrypoint-initdb.d/

EXPOSE 5432

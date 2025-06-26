CREATE TYPE role AS ENUM ('Administrator', 'User');

CREATE TABLE "user"
(
    id            TEXT PRIMARY KEY,
    name          TEXT        NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password      TEXT        NOT NULL,
    role          role        NOT NULL DEFAULT 'User',
    register_date TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE gps_track
(
    id        TEXT PRIMARY KEY,
    user_id   TEXT      REFERENCES "user" (id) ON DELETE SET NULL,
    latitude  TEXT      NOT NULL,
    longitude TEXT      NOT NULL,
    timestamp TIMESTAMP NOT NULL
);


CREATE TABLE cron_log
(
    id       SERIAL PRIMARY KEY,
    job_name TEXT,
    run_time TIMESTAMP NOT NULL,
    status   TEXT,
    message  TEXT
);


CREATE EXTENSION IF NOT EXISTS pg_cron;


SELECT cron.schedule(
               'delete_old_tracks',
               '0 3 * * *',
               $$
    DO $do$
    DECLARE
        deleted_count INT;
    BEGIN
        DELETE FROM gps_track WHERE timestamp < NOW() - INTERVAL '30 days';
        GET DIAGNOSTICS deleted_count = ROW_COUNT;

        INSERT INTO cron_log(job_name, run_time, status, message)
        VALUES ('delete_old_tracks', NOW(), 'ok', 'Deleted ' || deleted_count || ' old tracks');
    END;
    $do$
    $$
       );

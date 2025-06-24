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
    user_id   TEXT      NOT NULL,
    latitude  TEXT      NOT NULL,
    longitude TEXT      NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
);

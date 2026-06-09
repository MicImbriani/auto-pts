CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.test_results_landing (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT        NOT NULL,
    source_file     TEXT        NOT NULL,
    ingest_ts       TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- test case attributes from XML
    name            TEXT        NOT NULL,
    project         TEXT,
    status          TEXT,
    status_previous TEXT,
    regression      BOOLEAN,
    progress        BOOLEAN,
    new_case        BOOLEAN,
    duration        REAL,
    run_count       INTEGER,
    description     TEXT,
    test_start_time TIMESTAMPTZ,
    test_end_time   TIMESTAMPTZ,

    UNIQUE (run_id, name)
);

CREATE TABLE IF NOT EXISTS raw.ingested_files (
    id          BIGSERIAL   PRIMARY KEY,
    file_path   TEXT        NOT NULL UNIQUE,
    file_hash   TEXT        NOT NULL,
    ingest_ts   TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id      TEXT        NOT NULL
);

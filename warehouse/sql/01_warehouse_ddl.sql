CREATE SCHEMA IF NOT EXISTS analytics;

-- ── Dimensions ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS analytics.dim_run (
    run_sk          SERIAL      PRIMARY KEY,
    run_id          TEXT        NOT NULL UNIQUE,
    source_file     TEXT,
    ingest_ts       TIMESTAMPTZ,
    run_started_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS analytics.dim_test_case (
    test_case_sk    SERIAL      PRIMARY KEY,
    name            TEXT        NOT NULL UNIQUE,
    profile         TEXT,
    case_name       TEXT,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS analytics.dim_status (
    status_sk       SERIAL      PRIMARY KEY,
    status_code     TEXT        NOT NULL UNIQUE,
    is_pass         BOOLEAN     NOT NULL DEFAULT false,
    is_error        BOOLEAN     NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_sk         INTEGER     PRIMARY KEY,  -- YYYYMMDD
    full_date       DATE        NOT NULL,
    year            SMALLINT    NOT NULL,
    month           SMALLINT    NOT NULL,
    week            SMALLINT    NOT NULL,
    day_of_week     TEXT        NOT NULL
);

-- ── Fact ──────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS analytics.fact_test_result (
    result_sk       BIGSERIAL   PRIMARY KEY,
    run_sk          INTEGER     NOT NULL REFERENCES analytics.dim_run(run_sk),
    test_case_sk    INTEGER     NOT NULL REFERENCES analytics.dim_test_case(test_case_sk),
    status_sk       INTEGER     NOT NULL REFERENCES analytics.dim_status(status_sk),
    date_sk         INTEGER     REFERENCES analytics.dim_date(date_sk),

    duration_sec    REAL,
    run_count       INTEGER,
    status_previous TEXT,
    is_regression   BOOLEAN     NOT NULL DEFAULT false,
    is_progress     BOOLEAN     NOT NULL DEFAULT false,
    is_new          BOOLEAN     NOT NULL DEFAULT false,
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,

    UNIQUE (run_sk, test_case_sk)
);

-- indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_fact_run      ON analytics.fact_test_result(run_sk);
CREATE INDEX IF NOT EXISTS idx_fact_tc       ON analytics.fact_test_result(test_case_sk);
CREATE INDEX IF NOT EXISTS idx_fact_status   ON analytics.fact_test_result(status_sk);
CREATE INDEX IF NOT EXISTS idx_fact_regress  ON analytics.fact_test_result(is_regression) WHERE is_regression;

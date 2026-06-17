WITH final_attempts AS (
    SELECT
        run_id
        , test_case_name
        , profile
        , started_at
        , duration_ms
    FROM {{ ref('stg_test_results') }}
    WHERE is_final_attempt = TRUE
)

SELECT
    test_case_name
    , profile
    , run_id
    , started_at
    , duration_ms
    , round(avg(duration_ms) OVER (
        PARTITION BY test_case_name
        ORDER BY started_at
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
      ), 0)                                             AS rolling_avg_5_runs_ms
    , first_value(duration_ms) OVER (
        PARTITION BY test_case_name
        ORDER BY started_at
      )                                                 AS first_ever_duration_ms
    , round(
        (duration_ms - first_value(duration_ms) OVER (
            PARTITION BY test_case_name
            ORDER BY started_at
        ))::FLOAT
        / NULLIF(first_value(duration_ms) OVER (
            PARTITION BY test_case_name
            ORDER BY started_at
        ), 0) * 100
      , 1)                                              AS pct_change_from_first_run
FROM final_attempts
ORDER BY test_case_name, started_at

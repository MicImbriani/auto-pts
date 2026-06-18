WITH all_attempts AS (
    SELECT
        run_id
        , test_case_name
        , profile
        , started_at
        , duration_ms
        , attempt_number
        , is_final_attempt
    FROM {{ ref('stg_test_results') }}
),

final_attempts AS (
    SELECT
        test_case_name
        , run_id
        , started_at
        , duration_ms
    FROM all_attempts
    WHERE is_final_attempt = TRUE
)

SELECT
    a.test_case_name
    , a.profile
    , a.run_id
    , a.started_at
    , a.attempt_number
    , a.is_final_attempt
    , a.duration_ms

    -- rolling average and pct change apply to final attempts only
    , CASE WHEN a.is_final_attempt THEN
        round(avg(a.duration_ms) OVER (
            PARTITION BY a.test_case_name
            ORDER BY a.started_at
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 0)
      END                                                AS rolling_avg_5_runs_ms

    , CASE WHEN a.is_final_attempt THEN
        first_value(a.duration_ms) OVER (
            PARTITION BY a.test_case_name
            ORDER BY a.started_at
        )
      END                                                AS first_ever_duration_ms

    , CASE WHEN a.is_final_attempt THEN
        round(
            (a.duration_ms - first_value(a.duration_ms) OVER (
                PARTITION BY a.test_case_name
                ORDER BY a.started_at
            ))::FLOAT
            / NULLIF(first_value(a.duration_ms) OVER (
                PARTITION BY a.test_case_name
                ORDER BY a.started_at
            ), 0) * 100
        , 1)
      END                                                AS pct_change_from_first_run

FROM all_attempts a
ORDER BY a.test_case_name, a.started_at, a.attempt_number

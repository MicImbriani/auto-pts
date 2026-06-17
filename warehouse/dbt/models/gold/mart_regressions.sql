WITH history AS (
    SELECT * FROM {{ ref('mart_test_case_history') }}
),

with_previous AS (
    SELECT
        run_id
        , test_case_name
        , profile
        , started_at
        , final_verdict
        , is_pass
        , attempt_number
        , LAG(final_verdict) OVER (
            PARTITION BY test_case_name
            ORDER BY started_at
          ) AS previous_verdict
        , LAG(run_id) OVER (
            PARTITION BY test_case_name
            ORDER BY started_at
          ) AS previous_run_id
    FROM history
)

SELECT
    run_id
    , test_case_name
    , profile
    , started_at
    , final_verdict
    , previous_verdict
    , previous_run_id
    , CASE
        WHEN NOT is_pass AND previous_verdict = 'PASS' THEN TRUE
        ELSE FALSE
      END AS is_regression
    , CASE
        WHEN is_pass AND previous_verdict != 'PASS' AND previous_verdict IS NOT NULL THEN TRUE
        ELSE FALSE
      END AS is_progress
FROM with_previous

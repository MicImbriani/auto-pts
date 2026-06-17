WITH runs AS (
    SELECT DISTINCT run_id, min(started_at) AS run_started_at
    FROM {{ ref('stg_test_results') }}
    WHERE is_final_attempt = TRUE
    GROUP BY run_id
),

run_order AS (
    SELECT
        run_id
        , run_started_at
        , LAG(run_id) OVER (ORDER BY run_started_at)  AS previous_run_id
    FROM runs
),

test_cases_per_run AS (
    SELECT DISTINCT run_id, test_case_name, profile
    FROM {{ ref('stg_test_results') }}
    WHERE is_final_attempt = TRUE
)

SELECT
    ro.run_id                       AS current_run_id
    , ro.run_started_at
    , ro.previous_run_id
    , prev.test_case_name
    , prev.profile
FROM run_order ro
JOIN test_cases_per_run prev
    ON prev.run_id = ro.previous_run_id
LEFT JOIN test_cases_per_run curr
    ON curr.run_id = ro.run_id
    AND curr.test_case_name = prev.test_case_name
WHERE curr.test_case_name IS NULL
ORDER BY ro.run_started_at, prev.profile, prev.test_case_name

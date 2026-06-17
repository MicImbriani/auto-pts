WITH final_attempts AS (
    SELECT * FROM {{ ref('stg_test_results') }}
    WHERE is_final_attempt = TRUE
)

SELECT
    run_id
    , profile
    , min(started_at)                                               AS run_started_at
    , count(*)                                                      AS total_cases
    , sum(CASE WHEN is_pass THEN 1 ELSE 0 END)                     AS pass_count
    , sum(CASE WHEN NOT is_pass THEN 1 ELSE 0 END)                 AS fail_count
    , round(
        sum(CASE WHEN is_pass THEN 1 ELSE 0 END)::FLOAT
        / count(*) * 100
      , 1)                                                          AS pass_rate_pct
FROM final_attempts
GROUP BY run_id, profile
ORDER BY run_id, profile

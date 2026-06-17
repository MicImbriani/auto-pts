WITH per_run AS (
    SELECT
        test_case_name
        , profile
        , run_id
        , max(attempt_number)                           AS attempts_in_run
        , max(CASE WHEN is_final_attempt THEN is_pass END) AS passed_eventually
        , min(CASE WHEN is_pass THEN attempt_number END)   AS first_pass_attempt
    FROM {{ ref('stg_test_results') }}
    GROUP BY test_case_name, profile, run_id
)

SELECT
    test_case_name
    , profile
    , count(*)                                          AS total_runs
    , sum(CASE WHEN attempts_in_run > 1 THEN 1 ELSE 0 END)
                                                        AS runs_with_retries
    , round(
        sum(CASE WHEN attempts_in_run > 1 THEN 1 ELSE 0 END)::FLOAT
        / count(*) * 100
      , 1)                                              AS retry_rate_pct
    , round(avg(attempts_in_run), 2)                   AS avg_attempts_per_run
    , max(attempts_in_run)                              AS max_attempts_in_single_run
    , sum(CASE WHEN passed_eventually THEN 1 ELSE 0 END)
                                                        AS runs_passed_eventually
    , sum(CASE WHEN first_pass_attempt = 1 THEN 1 ELSE 0 END)
                                                        AS runs_passed_first_attempt
    , round(
        sum(CASE WHEN first_pass_attempt = 1 THEN 1 ELSE 0 END)::FLOAT
        / count(*) * 100
      , 1)                                              AS first_attempt_pass_rate_pct
FROM per_run
GROUP BY test_case_name, profile
ORDER BY retry_rate_pct DESC, test_case_name

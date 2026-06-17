SELECT
    run_id
    , test_case_name
    , profile
    , started_at
    , final_verdict
    , is_pass
    , attempt_number
    , pts_version
FROM {{ ref('stg_test_results') }}
WHERE is_final_attempt = TRUE

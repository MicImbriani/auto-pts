WITH base AS (
   SELECT file_path
, run_id
, ingested_at
, test_case_name
, profile
, pts_version
, final_verdict
, pics_pixit_raw
, started_at::TIMESTAMP
, duration_ms::INTEGER
, CASE WHEN final_verdict = 'PASS' THEN TRUE ELSE FALSE END AS is_pass
, ROW_NUMBER() OVER(partition BY test_case_name, run_id ORDER BY started_at ) AS attempt_number
FROM {{ source('bronze', 'bronze_test_results')}}
)

SELECT
    *
    , attempt_number = MAX(attempt_number) OVER (PARTITION BY run_id, test_case_name) AS is_final_attempt
FROM base

-- Fails if any test case has a non-positive duration
SELECT *
FROM {{ ref('stg_test_results') }}
WHERE duration_ms <= 0

-- Fails if any attempt_number is less than 1
SELECT *
FROM {{ ref('stg_test_results') }}
WHERE attempt_number < 1

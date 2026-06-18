-- Fails if any (run_id, test_case_name) has more than one final attempt
SELECT run_id, test_case_name, count(*) AS cnt
FROM {{ ref('stg_test_results') }}
WHERE is_final_attempt = TRUE
GROUP BY run_id, test_case_name
HAVING count(*) > 1

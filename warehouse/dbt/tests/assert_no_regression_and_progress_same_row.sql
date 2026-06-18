-- Fails if any row is marked as both a regression and a progress simultaneously
SELECT *
FROM {{ ref('mart_regressions') }}
WHERE is_regression = TRUE AND is_progress = TRUE

-- Fails if any profile in any run has a pass rate outside 0-100%
SELECT *
FROM {{ ref('mart_profile_passrate') }}
WHERE pass_rate_pct < 0 OR pass_rate_pct > 100

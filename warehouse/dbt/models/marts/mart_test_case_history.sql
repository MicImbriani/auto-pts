-- Trend view: full status timeline per test case
select
    tc.name,
    tc.profile,
    tc.case_name,
    dr.run_started_at,
    ds.status_code,
    f.status_previous,
    f.is_regression,
    f.is_progress,
    f.is_new,
    f.duration_sec,
    f.run_count
from {{ ref('fact_test_result') }} f
join {{ ref('dim_run') }}       dr  on dr.run_sk       = f.run_sk
join {{ ref('dim_test_case') }} tc  on tc.test_case_sk = f.test_case_sk
join {{ ref('dim_status') }}    ds  on ds.status_sk    = f.status_sk
order by tc.name, dr.run_started_at

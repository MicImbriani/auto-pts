-- Regressions in the most recent run
with latest_run as (
    select run_sk
    from {{ ref('dim_run') }}
    order by run_started_at desc nulls last
    limit 1
)

select
    tc.name,
    tc.profile,
    tc.case_name,
    f.status_previous,
    ds.status_code  as current_status,
    dr.run_started_at
from {{ ref('fact_test_result') }} f
join latest_run                      lr  on lr.run_sk       = f.run_sk
join {{ ref('dim_run') }}            dr  on dr.run_sk       = f.run_sk
join {{ ref('dim_test_case') }}      tc  on tc.test_case_sk = f.test_case_sk
join {{ ref('dim_status') }}         ds  on ds.status_sk    = f.status_sk
where f.is_regression
order by tc.profile, tc.name

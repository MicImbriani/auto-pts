-- CI gate: pass-rate per profile for the most recent run
with latest_run as (
    select run_sk
    from {{ ref('dim_run') }}
    order by run_started_at desc nulls last
    limit 1
)

select
    tc.profile,
    count(*)                                              as total_cases,
    sum(case when ds.is_pass then 1 else 0 end)           as pass_count,
    sum(case when ds.is_pass then 1 else 0 end)::real
        / nullif(count(*), 0) * 100                       as pass_rate_pct,
    dr.run_started_at
from {{ ref('fact_test_result') }} f
join latest_run                      lr  on lr.run_sk     = f.run_sk
join {{ ref('dim_run') }}            dr  on dr.run_sk     = f.run_sk
join {{ ref('dim_test_case') }}      tc  on tc.test_case_sk = f.test_case_sk
join {{ ref('dim_status') }}         ds  on ds.status_sk  = f.status_sk
group by tc.profile, dr.run_started_at
order by tc.profile

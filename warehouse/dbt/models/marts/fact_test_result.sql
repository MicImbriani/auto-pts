select
    {{ dbt_utils.generate_surrogate_key(['s.run_id', 's.name']) }} as result_sk,

    dr.run_sk,
    dtc.test_case_sk,
    ds.status_sk,
    s.date_sk,

    s.duration_sec,
    s.run_count,
    s.status_previous,
    s.is_regression,
    s.is_progress,
    s.is_new,
    s.started_at,
    s.ended_at

from {{ ref('stg_test_results') }} s

left join {{ ref('dim_run') }}       dr  on dr.run_id       = s.run_id
left join {{ ref('dim_test_case') }} dtc on dtc.name        = s.name
left join {{ ref('dim_status') }}    ds  on ds.status_code  = s.status

-- SCD-1: last-write-wins on description
select distinct on (name)
    {{ dbt_utils.generate_surrogate_key(['name']) }} as test_case_sk,
    name,
    profile,
    case_name,
    description
from {{ ref('stg_test_results') }}
order by name, started_at desc nulls last

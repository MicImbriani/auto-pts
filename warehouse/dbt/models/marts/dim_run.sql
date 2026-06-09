{{
  config(
    unique_key = 'run_id',
    incremental_strategy = 'merge'
  )
}}

select
    {{ dbt_utils.generate_surrogate_key(['run_id']) }} as run_sk,
    run_id,
    source_file,
    ingest_ts,
    run_started_at
from {{ ref('stg_runs') }}

{% if is_incremental() %}
where run_id not in (select run_id from {{ this }})
{% endif %}

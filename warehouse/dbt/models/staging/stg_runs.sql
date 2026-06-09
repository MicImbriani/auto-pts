-- One row per distinct run_id
select distinct
    run_id,
    source_file,
    min(ingest_ts)       over (partition by run_id) as ingest_ts,
    min(started_at)      over (partition by run_id) as run_started_at
from {{ ref('stg_test_results') }}

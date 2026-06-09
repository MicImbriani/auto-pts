-- Staging: clean and cast raw landing rows
with source as (
    select * from raw.test_results_landing
),

cleaned as (
    select
        run_id,
        source_file,
        ingest_ts,

        name,
        coalesce(project, split_part(name, '/', 1))             as profile,
        case
            when name like '%/%' then split_part(name, '/', 2)
            else name
        end                                                      as case_name,

        status,
        nullif(status_previous, 'None')                         as status_previous,
        coalesce(regression, false)                              as is_regression,
        coalesce(progress, false)                                as is_progress,
        coalesce(new_case, false)                                as is_new,

        duration                                                 as duration_sec,
        run_count,
        description,
        test_start_time                                          as started_at,
        test_end_time                                            as ended_at,

        -- date key for dim_date (YYYYMMDD integer)
        to_char(test_start_time, 'YYYYMMDD')::integer           as date_sk

    from source
)

select * from cleaned

-- Date dimension populated from dates present in the facts
select distinct
    date_sk,
    (to_char(started_at, 'YYYYMMDD')::integer)::text::date          as full_date,
    extract(year  from started_at)::smallint                         as year,
    extract(month from started_at)::smallint                         as month,
    extract(week  from started_at)::smallint                         as week,
    to_char(started_at, 'Day')                                       as day_of_week
from {{ ref('stg_test_results') }}
where date_sk is not null

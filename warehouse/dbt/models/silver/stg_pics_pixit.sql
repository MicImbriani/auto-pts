WITH lines AS (
    SELECT
        file_path
        , run_id
        , unnest(string_split(pics_pixit_raw, chr(10))) AS line
    FROM {{ ref('stg_test_results') }}
),

filtered AS (
    SELECT
        file_path
        , run_id
        , trim(line) AS line
    FROM lines
    WHERE
        trim(line) != ''
        AND trim(line) NOT LIKE 'ICS VALUES%'
        AND trim(line) NOT LIKE 'IXIT VALUES%'
        AND trim(line) NOT LIKE 'Test Case Started%'
),

split AS (
    SELECT
        file_path
        , run_id
        , trim(split_part(line, ' ', 1)) AS parameter_name
        , trim(substr(line, length(split_part(line, ' ', 1)) + 2)) AS parameter_value
    FROM filtered
    WHERE line LIKE 'TSPC_%' OR line LIKE 'TSPX_%'
)

SELECT
    file_path
    , run_id
    , parameter_name
    , parameter_value
    , CASE
        WHEN parameter_name LIKE 'TSPC_%' THEN 'ICS'
        WHEN parameter_name LIKE 'TSPX_%' THEN 'IXIT'
      END AS parameter_type
FROM split

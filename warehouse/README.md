# AutoPTS Warehouse

## Setup

```bash
pip install -r requirements.txt
```

## Ingest a run

```bash
python -m warehouse.ingest.run <CI_JOB_ID> <path/to/run/folder>
```

The run folder must contain an `XMLs/` subdirectory with PTS log XML files.

The database path is set via a required environment variable:

```bash
export AUTOPTS_WH_PATH=/path/to/autopts_warehouse.duckdb
```

This must be set before running both the ingest script and dbt commands.

## Run dbt transforms

**Important:** dbt must be told where to find `profiles.yml` since it lives
in the project folder rather than `~/.dbt/`. Always pass `--profiles-dir .`
when running dbt commands:

```bash
cd warehouse/dbt
dbt run --profiles-dir .
dbt test --profiles-dir .
```

## Run tests

```bash
python -m pytest warehouse/tests/
```

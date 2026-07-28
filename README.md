# HTAG Data Pipeline

This package extracts property-market data from the HTAG API, stores versioned
raw responses, transforms them into CSV files, and optionally upserts the
cleaned rows into Supabase.

## Execution flow

`run_htag_pipeline.py` runs the stages in this order:

```text
HTAG API
   |
   v
ingest localities -> clean localities
                         |
                         v
               ingest market endpoints
                         |
                         v
               clean market endpoints
                         |
                         v
        upload localities and market endpoints
                         |
                         v
                      Supabase
```

Each stage can be enabled or disabled per dataset in `pipeline_config.yml`.
The top-level `upload=False` Python argument is an additional safety switch
that disables every upload, regardless of the YAML settings.

## Repository layout

```text
htag_data_pipeline/
|-- run_htag_pipeline.py       Main orchestration entry point
|-- pipeline_config.yml        Per-dataset ingest/clean/upload switches
|-- pipeline_config.py         Loads and validates pipeline_config.yml
|-- config.py                  Environment and connection settings
|-- endpoints.py               Authoritative HTAG endpoint metadata
|-- htag_client.py             HTTP requests, pagination, and rate limiting
|-- json_storage.py            Raw JSON folder naming and versioning
|-- logging_utils.py           Per-run file logging
|-- pipelines/
|   |-- ingest.py              API-to-raw-JSON workflows
|   |-- clean.py               Raw-JSON-to-clean-CSV workflows
|   `-- upload.py              Clean-CSV-to-Supabase workflows
|-- transformers/
|   |-- __utils__.py           Shared data discovery and CSV helpers
|   |-- localities.py          Locality cleaning rules
|   |-- market_endpoints.py    Shared market cleaning rules
|   |-- market_registry.py     Maps API paths to transformers
|   `-- market_*.py            Dataset-specific columns and transformers
|-- outbound/
|   |-- __utils__.py           Supabase client, batching, and upserts
|   |-- localities.py          Locality upload mapping
|   |-- endpoints.py           Market endpoint upload mapping
|   `-- create_sql_tables.sql  Supabase/PostgreSQL table definitions
|-- data/                      Generated raw and clean data (Git-ignored)
|-- logging/                   Generated run logs (Git-ignored)
`-- .env                       Local secrets (Git-ignored)
```

The `__init__.py` files make the directories importable Python packages and
re-export commonly used functions. `__utils__.py` files contain internal
helpers shared by modules in the same layer.

## Configuration

There are three configuration sources. They have different responsibilities
and are not interchangeable.

### 1. `.env`: credentials

Create `.env` in the package root with:

```dotenv
HTAG_API_KEY=your-htag-api-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
```

| Variable | Used by | Effect |
|---|---|---|
| `HTAG_API_KEY` | `config.py`, `htag_client.py` | Sent as the `x-api-key` header. Ingest requests will fail if it is absent or invalid. |
| `SUPABASE_URL` | `outbound/__utils__.py` | Selects the Supabase project used by upload stages. |
| `SUPABASE_KEY` | `outbound/__utils__.py` | Authenticates Supabase upserts. It must have write access to the configured schema and tables. |

`SUPABASE_SERVICE_KEY` is read in `config.py`, but the current uploader does
not use it; uploads use `SUPABASE_KEY`. Never commit `.env`.

Connection constants in `config.py` also affect execution:

| Setting | Current value | Effect |
|---|---|---|
| `HTAG_BASE_URL` | `https://api.htagai.com/v1` | Base URL prepended to every HTAG endpoint path. |
| `SUPABASE_SCHEMA` | `investitgroup` | Schema targeted by all Supabase upserts. |
| `ENDPOINT_TABLE_MAP` | locality mapping | Maps the special locality dataset to its table. |

### 2. `pipeline_config.yml`: stage switches

Every dataset has this shape:

```yaml
pipelines:
  trends_price:
    path: /markets/trends/price
    table: market_trend_price
    ingest: N
    clean: Y
    upload: Y
```

The three switches accept only uppercase `Y` or `N`:

| Switch | `Y` means | `N` means |
|---|---|---|
| `ingest` | Call HTAG and write a new raw `vNNN/response.json`. | Reuse raw data already on disk. |
| `clean` | Read raw versions and overwrite `clean/response.csv`. | Reuse the clean CSV already on disk. |
| `upload` | Upsert the clean CSV when the run's `upload` argument is also `True`. | Do not upload that dataset. |

Important details:

- `path` links the YAML entry to an endpoint in `endpoints.py`. It must match
  exactly.
- `table` in this YAML file is currently descriptive only. Uploads obtain the
  actual table name from `endpoints.py`.
- The `locality` entry is handled specially by name; market entries are
  matched by `path`.
- A market endpoint that is missing from the YAML, or whose `path` no longer
  matches, defaults to enabled for all stages. Keep the YAML and
  `endpoints.py` synchronized.
- All three switches are required for every YAML entry. Invalid or lowercase
  values stop the run during configuration validation.
- A custom file can be supplied with
  `run_all_pipelines(config_path="path/to/config.yml")`.

The checked-in configuration currently disables all ingestion and enables
cleaning and uploading. It therefore expects compatible raw files to already
exist under the selected run date.

### 3. `endpoints.py`: endpoint behavior

`ENDPOINTS` is the authoritative market-endpoint registry. Each dictionary
controls:

| Key | Effect |
|---|---|
| `path` | HTAG URL path, transformer lookup, local folder name, and YAML switch matching. |
| `table` | Supabase destination table and a fallback local folder name. |
| `params.limit` / `params.offset` | Initial API pagination settings. |
| `params.area_id` | Its presence enables batched area-ID requests. |
| `params.level` | HTAG geographic level sent with the request. |
| `on_conflict` | Columns used to deduplicate clean/upload rows and form the Supabase upsert conflict target. |
| `batch_size` | Optional area-ID request batch size; defaults to `500`. |
| `timeout` | Optional HTTP timeout in seconds; defaults to `30`. |
| `pagination_sleep_seconds` | Optional delay between pages; defaults to `0.2`. |
| `columns` | Optional upload column allow-list. If omitted, every cleaned column except `_source_file` is uploaded. |

Adding an endpoint requires more than a YAML entry. Add its metadata to
`ENDPOINTS`, create or reuse a transformer, register the path in
`transformers/market_registry.py`, add a YAML entry, and ensure the matching
database table and conflict constraint exist.

## Data folders

Generated data is organized by run date and API path:

```text
data/
`-- YYYYMMDD/
    |-- locality/
    |   |-- raw/
    |   |   |-- v001/response.json
    |   |   `-- v002/response.json
    |   `-- clean/response.csv
    `-- markets_trends_price/
        |-- raw/
        |   `-- v001/response.json
        `-- clean/response.csv
```

API paths are converted to lowercase underscore-separated folders. For
example, `/markets/trends/price` becomes `markets_trends_price`.

- Ingest never overwrites raw data. It creates the next `vNNN` directory.
- Clean uses `version="all"` in the main runner, combines every raw version
  for that run date, and overwrites the single clean CSV.
- When a helper is called without `run_date`, it selects the newest directory
  named `YYYYMMDD` or `YYYY-MM-DD`.
- The main runner does pass a date—today by default—so disabled ingestion
  requires raw files under today's directory unless another `run_date` is
  supplied.
- Endpoint ingestion first reads
  `data/<run_date>/locality/clean/response.csv`. `locality_limit` limits how
  many rows it uses; the main runner defaults to `500`.

## Running the pipeline

The code requires Python plus `pandas`, `requests`, `python-dotenv`, and
`supabase`. `PyYAML` is optional because the project includes a parser for the
small YAML subset used here.

Run from the directory that contains the `htag_data_pipeline` package:

```powershell
python -m htag_data_pipeline.run_htag_pipeline
```

The script uses today's `YYYYMMDD` date, the `data` directory, the default
`pipeline_config.yml`, and enables upload. For a safer local clean-only run:

```powershell
python -c "from htag_data_pipeline.run_htag_pipeline import run_all_pipelines; run_all_pipelines(run_date='20260625', upload=False)"
```

Common Python arguments:

| Argument | Default | Effect |
|---|---|---|
| `data_dir` | `"data"` | Root directory for raw and clean files. Relative paths are resolved from the current working directory. |
| `run_date` | today as `YYYYMMDD` | Date directory read and written by the run. |
| `upload` | `True` | Global upload safety switch. |
| `config_path` | package `pipeline_config.yml` | Alternative stage-switch file. |
| `locality_limit` | `500` | Maximum cleaned localities used for market endpoint ingestion. |

`run_all_pipelines()` returns `True` on success and `False` when orchestration
handles a failure. The `__main__` block does not currently convert that value
to a non-zero process exit code.

## Upload and database behavior

Uploads read each clean CSV as strings, convert missing values to JSON `null`,
deduplicate on the configured conflict columns, and send batches of 1,000 by
default. Supabase performs upserts into the `investitgroup` schema.

Run `outbound/create_sql_tables.sql` in the target database before enabling
uploads. Table names and primary/unique constraints must agree with
`endpoints.py`; otherwise an upsert can fail even when ingestion and cleaning
succeed.

## Logs and failure behavior

Each run creates:

```text
logging/htag_data_pipeline_YYYYMMDD_HH_MM_SSAM_pipeline.log
```

Progress is also printed to the console. Detailed exceptions, failed HTTP
responses, row counts, and output paths are written to the log.

The orchestrator stops when locality ingestion or locality cleaning fails.
Unexpected exceptions in later stages are caught, logged, and cause
`run_all_pipelines()` to return `False`. A failed market API request can
produce an empty raw response for that endpoint, so inspect the log and row
counts after a run rather than relying only on the final success message.

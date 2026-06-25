import logging
from pathlib import Path

from htag_data_pipeline.config import SUPABASE_SCHEMA
from htag_data_pipeline.endpoints import ENDPOINTS
from htag_data_pipeline.json_storage import endpoint_to_folder
from htag_data_pipeline.outbound.__utils__ import (
    dataframe_to_records,
    read_clean_csv,
    upsert_records,
)


logger = logging.getLogger(__name__)


def get_endpoint_upload_config(endpoint):
    """Return endpoint upload metadata for an endpoint dict or API path."""
    if isinstance(endpoint, dict):
        return endpoint

    for endpoint_config in ENDPOINTS:
        if endpoint_config.get("path") == endpoint:
            return endpoint_config

    raise ValueError(f"Endpoint is not configured in endpoints.py: {endpoint}")


def normalize_on_conflict(on_conflict):
    """Convert endpoint on_conflict config into the format expected by Supabase."""
    if isinstance(on_conflict, (list, tuple)):
        return ",".join(on_conflict)
    return on_conflict


def endpoint_folder_candidates(endpoint_config):
    """Return possible local folder names for an endpoint config."""
    endpoint = endpoint_config.get("endpoint")
    if endpoint:
        return [endpoint]

    path = endpoint_config.get("path")
    if not path:
        raise ValueError("Endpoint config must include 'path' or 'endpoint'")

    endpoint_folder = endpoint_to_folder(path)
    table = endpoint_config.get("table")
    singular_market = endpoint_folder.replace("markets_", "market_", 1)
    candidates = [endpoint_folder, table, singular_market]
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def endpoint_clean_folder(endpoint_config, data_dir="data", run_date=None):
    """Return the clean data folder name for an endpoint config."""
    if run_date:
        date_dir = Path(data_dir) / str(run_date)
    else:
        from htag_data_pipeline.transformers.__utils__ import find_latest_date_dir

        date_dir = find_latest_date_dir(data_dir)

    candidates = endpoint_folder_candidates(endpoint_config)
    for folder in candidates:
        if (date_dir / folder / "raw").exists() and (date_dir / folder / "clean").exists():
            return folder

    for folder in candidates:
        if (date_dir / folder / "clean").exists():
            return folder

    return candidates[0]


def load_clean_endpoint_data(endpoint, data_dir="data", run_date=None):
    """Read an endpoint clean CSV into a DataFrame."""
    endpoint_config = get_endpoint_upload_config(endpoint)
    endpoint_folder = endpoint_clean_folder(endpoint_config, data_dir=data_dir, run_date=run_date)
    logger.info(
        "Activity started | activity=load_clean_endpoint_data | endpoint=%s | folder=%s | data_dir=%s | run_date=%s",
        endpoint_config.get("path"),
        endpoint_folder,
        data_dir,
        run_date,
    )
    df = read_clean_csv(data_dir=data_dir, endpoint=endpoint_folder, run_date=run_date)
    logger.info(
        "Activity completed | activity=load_clean_endpoint_data | endpoint=%s | rows=%s",
        endpoint_config.get("path"),
        len(df),
    )
    return df


def endpoint_dataframe_to_records(df, endpoint):
    """Convert an endpoint clean DataFrame into upload records."""
    endpoint_config = get_endpoint_upload_config(endpoint)
    columns = endpoint_config.get("columns")
    on_conflict = endpoint_config.get("on_conflict")

    if "_source_file" in df.columns:
        df = df.drop(columns=["_source_file"])
        logger.info("Dropped upload-only source column | endpoint=%s | column=_source_file", endpoint_config.get("path"))

    if on_conflict:
        dedupe_columns = list(on_conflict) if isinstance(on_conflict, (list, tuple)) else [on_conflict]
        before_deduplicate = len(df)
        df = df.drop_duplicates(subset=dedupe_columns, keep="last")
        dropped_duplicates = before_deduplicate - len(df)
        if dropped_duplicates:
            logger.info(
                "Dropped duplicate endpoint upload records | endpoint=%s | rows=%s | subset=%s",
                endpoint_config.get("path"),
                dropped_duplicates,
                dedupe_columns,
            )

    return dataframe_to_records(df, columns=columns)


def push_endpoint_to_supabase(endpoint, data_dir="data", run_date=None, batch_size=1000):
    """Read one endpoint clean CSV and upsert it into its configured Supabase table."""

    endpoint_config = get_endpoint_upload_config(endpoint)
    table_name = endpoint_config.get("table")
    if not table_name:
        raise ValueError(f"Endpoint config missing 'table': {endpoint_config}")

    on_conflict = normalize_on_conflict(endpoint_config.get("on_conflict"))
    logger.info(
        "Activity started | activity=push_endpoint_to_supabase | endpoint=%s | table=%s | on_conflict=%s | data_dir=%s | run_date=%s | batch_size=%s",
        endpoint_config.get("path"),
        table_name,
        on_conflict,
        data_dir,
        run_date,
        batch_size,
    )

    df = load_clean_endpoint_data(endpoint_config, data_dir=data_dir, run_date=run_date)
    
    records = endpoint_dataframe_to_records(df, endpoint_config)
    responses = upsert_records(
        schema=SUPABASE_SCHEMA,
        table_name=table_name,
        records=records,
        batch_size=batch_size,
        on_conflict=on_conflict,
    )
    uploaded_count = sum(getattr(response, "count", 0) or 0 for response in responses)
    logger.info(
        "Activity completed | activity=push_endpoint_to_supabase | endpoint=%s | table=%s | batches=%s | uploaded_count=%s",
        endpoint_config.get("path"),
        table_name,
        len(responses),
        uploaded_count,
    )
    return responses


def push_all_endpoints_to_supabase(endpoints=None, data_dir="data", run_date=None, batch_size=1000):
    """Upload every configured endpoint clean CSV to Supabase."""
    responses_by_endpoint = {}

    for endpoint_config in endpoints or ENDPOINTS:
        endpoint_path = endpoint_config["path"]
        responses_by_endpoint[endpoint_path] = push_endpoint_to_supabase(
            endpoint_config,
            data_dir=data_dir,
            run_date=run_date,
            batch_size=batch_size,
        )

    return responses_by_endpoint

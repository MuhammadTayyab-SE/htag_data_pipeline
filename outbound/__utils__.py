import logging
from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


logger = logging.getLogger(__name__)


def load_supabase_env():
    """Load Supabase env vars from package .env and current working directory."""
    package_env = Path(__file__).resolve().parents[1] / ".env"
    if package_env.exists():
        load_dotenv(package_env)
        logger.info("Loaded Supabase environment file | file=%s", package_env)
    else:
        logger.warning("Package .env file not found | file=%s", package_env)

    load_dotenv()


def get_supabase_client():
    """Create a Supabase client using SUPABASE_URL and SUPABASE_KEY."""

    logger.info("Activity started | activity=get_supabase_client")
    load_supabase_env()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        logger.error("SUPABASE_URL is missing from environment")
        raise ValueError("SUPABASE_URL is missing from .env")
    if not supabase_key:
        logger.error("SUPABASE_KEY is missing from environment")
        raise ValueError("SUPABASE_KEY is missing from .env")

    logger.info("Activity completed | activity=get_supabase_client | supabase_url_configured=%s | supabase_key_configured=%s", bool(supabase_url), bool(supabase_key))
    return create_client(supabase_url, supabase_key)


def read_clean_csv(data_dir="data", endpoint=None, run_date=None, file_name="response.csv"):
    """Read data/date/endpoint/clean/response.csv into a DataFrame."""
    if not endpoint:
        raise ValueError("endpoint is required, for example endpoint='locality'")

    if run_date is None:
        from htag_data_pipeline.transformers.__utils__ import find_latest_date_dir

        date_dir = find_latest_date_dir(data_dir)
    else:
        date_dir = Path(data_dir) / str(run_date)

    file_path = date_dir / endpoint / "clean" / file_name
    logger.info("Activity started | activity=read_clean_csv | endpoint=%s | file=%s", endpoint, file_path)
    if not file_path.exists():
        logger.error("Clean CSV file not found | endpoint=%s | file=%s", endpoint, file_path)
        raise FileNotFoundError(f"Clean CSV file not found: {file_path}")

    df = pd.read_csv(file_path, dtype="string")
    logger.info("Activity completed | activity=read_clean_csv | endpoint=%s | rows=%s | file=%s", endpoint, len(df), file_path)
    return df


def dataframe_to_records(df, columns=None):
    """Convert a DataFrame to JSON-safe dict records."""
    logger.info("Activity started | activity=dataframe_to_records | rows=%s", len(df))
    if columns is not None:
        missing_columns = [column for column in columns if column not in df.columns]
        if missing_columns:
            missing = ", ".join(missing_columns)
            logger.error("Missing required dataframe columns | columns=%s", missing)
            raise ValueError(f"Missing required column(s): {missing}")
        df = df[columns]

    cleaned = df.astype(object).where(pd.notna(df), None)
    records = cleaned.to_dict(orient="records")
    logger.info("Activity completed | activity=dataframe_to_records | records=%s", len(records))
    return records


def chunks(items, size):
    """Yield fixed-size chunks from a list."""
    for index in range(0, len(items), size):
        yield items[index:index + size]


def upsert_records(schema, table_name, records, batch_size=1000, on_conflict=None, supabase=None):
    """Upsert records into a Supabase table in batches."""
    if not records:
        logger.warning("No records to upsert | schema=%s | table=%s", schema, table_name)
        return []

    logger.info(
        "Activity started | activity=upsert_records | schema=%s | table=%s | records=%s | batch_size=%s | on_conflict=%s",
        schema,
        table_name,
        len(records),
        batch_size,
        on_conflict,
    )
    supabase = supabase or get_supabase_client()
    responses = []
    
    for batch_number, batch in enumerate(chunks(records, batch_size), start=1):
        logger.info("Supabase upsert batch started | schema=%s | table=%s | batch=%s | records=%s", schema, table_name, batch_number, len(batch))
        if on_conflict:
            query = supabase.schema(schema).table(table_name).upsert(batch, on_conflict=on_conflict, count="exact")
        else:
            query = supabase.schema(schema).table(table_name).upsert(batch, count="exact")
        response = query.execute()
        responses.append(response)
        logger.info(
            "Supabase upsert batch completed | schema=%s | table=%s | batch=%s | reported_count=%s",
            schema,
            table_name,
            batch_number,
            getattr(response, "count", None),
        )

    uploaded_count = sum(getattr(response, "count", 0) or 0 for response in responses)
    logger.info(
        "Activity completed | activity=upsert_records | schema=%s | table=%s | batches=%s | uploaded_count=%s",
        schema,
        table_name,
        len(responses),
        uploaded_count,
    )
    return responses

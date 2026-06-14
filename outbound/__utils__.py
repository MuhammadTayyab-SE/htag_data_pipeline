from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client


def load_supabase_env():
    """Load Supabase env vars from package .env and current working directory."""
    package_env = Path(__file__).resolve().parents[1] / ".env"
    if package_env.exists():
        load_dotenv(package_env)

    load_dotenv()


def get_supabase_client():
    """Create a Supabase client using SUPABASE_URL and SUPABASE_KEY."""

    load_supabase_env()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError("SUPABASE_URL is missing from .env")
    if not supabase_key:
        raise ValueError("SUPABASE_KEY is missing from .env")

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
    if not file_path.exists():
        raise FileNotFoundError(f"Clean CSV file not found: {file_path}")

    return pd.read_csv(file_path, dtype="string")


def dataframe_to_records(df, columns=None):
    """Convert a DataFrame to JSON-safe dict records."""
    if columns is not None:
        missing_columns = [column for column in columns if column not in df.columns]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise ValueError(f"Missing required column(s): {missing}")
        df = df[columns]

    cleaned = df.astype(object).where(pd.notna(df), None)
    return cleaned.to_dict(orient="records")


def chunks(items, size):
    """Yield fixed-size chunks from a list."""
    for index in range(0, len(items), size):
        yield items[index:index + size]


def upsert_records(schema, table_name, records, batch_size=1000, on_conflict=None, supabase=None):
    """Upsert records into a Supabase table in batches."""
    if not records:
        return []

    supabase = supabase or get_supabase_client()
    responses = []

    for batch in chunks(records, batch_size):
        if on_conflict:
            query = supabase.schema(schema).table(table_name).upsert(batch, on_conflict=on_conflict)
        else:
            query = supabase.schema(schema).table(table_name).upsert(batch)
        responses.append(query.execute())

    return responses

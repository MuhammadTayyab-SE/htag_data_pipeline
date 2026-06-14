from htag_data_pipeline.config import ENDPOINT_TABLE_MAP, SUPABASE_SCHEMA
from htag_data_pipeline.outbound.__utils__ import (
    dataframe_to_records,
    read_clean_csv,
    upsert_records,
)


LOCALITY_ENDPOINT = "locality"
LOCALITY_COLUMNS = [
    "loc_pid",
    "locality",
    "postcode",
    "state_name",
    "suburb_key",
    "lga_pid_ref",
]


def load_clean_localities(data_dir="data", run_date=None):
    """Load clean locality CSV data."""
    return read_clean_csv(data_dir=data_dir, endpoint=LOCALITY_ENDPOINT, run_date=run_date)


def clean_localities_to_records(df):
    """Convert clean locality DataFrame rows into Supabase records."""
    df = df[LOCALITY_COLUMNS].drop_duplicates(subset=["loc_pid"], keep="last")
    return dataframe_to_records(df, columns=LOCALITY_COLUMNS)


def push_localities_to_supabase(data_dir="data", run_date=None, batch_size=1000):
    """Read clean localities and upsert them into the localities Supabase table."""
    df = load_clean_localities(data_dir=data_dir, run_date=run_date)
    records = clean_localities_to_records(df)
    return upsert_records(
        schema=SUPABASE_SCHEMA,
        table_name=ENDPOINT_TABLE_MAP[LOCALITY_ENDPOINT],
        records=records,
        batch_size=batch_size,
        on_conflict="loc_pid",
    )

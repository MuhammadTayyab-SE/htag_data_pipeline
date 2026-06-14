import logging

from htag_data_pipeline.config import ENDPOINT_TABLE_MAP, SUPABASE_SCHEMA
from htag_data_pipeline.outbound.__utils__ import (
    dataframe_to_records,
    read_clean_csv,
    upsert_records,
)


logger = logging.getLogger(__name__)


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
    logger.info("Activity started | activity=load_clean_localities | data_dir=%s | run_date=%s", data_dir, run_date)
    return read_clean_csv(data_dir=data_dir, endpoint=LOCALITY_ENDPOINT, run_date=run_date)


def clean_localities_to_records(df):
    """Convert clean locality DataFrame rows into Supabase records."""
    logger.info("Activity started | activity=clean_localities_to_records | input_rows=%s", len(df))
    before_deduplicate = len(df)
    df = df[LOCALITY_COLUMNS].drop_duplicates(subset=["loc_pid"], keep="last")
    dropped_duplicates = before_deduplicate - len(df)
    if dropped_duplicates:
        logger.info("Dropped duplicate upload records | rows=%s | subset=loc_pid", dropped_duplicates)
    records = dataframe_to_records(df, columns=LOCALITY_COLUMNS)
    logger.info("Activity completed | activity=clean_localities_to_records | records=%s", len(records))
    return records


def push_localities_to_supabase(data_dir="data", run_date=None, batch_size=1000):
    """Read clean localities and upsert them into the localities Supabase table."""
    logger.info(
        "Activity started | activity=push_localities_to_supabase | data_dir=%s | run_date=%s | batch_size=%s",
        data_dir,
        run_date,
        batch_size,
    )
    df = load_clean_localities(data_dir=data_dir, run_date=run_date)
    records = clean_localities_to_records(df)
    responses = upsert_records(
        schema=SUPABASE_SCHEMA,
        table_name=ENDPOINT_TABLE_MAP[LOCALITY_ENDPOINT],
        records=records,
        batch_size=batch_size,
        on_conflict="loc_pid",
    )
    uploaded_count = sum(getattr(response, "count", 0) or 0 for response in responses)
    logger.info(
        "Activity completed | activity=push_localities_to_supabase | batches=%s | uploaded_count=%s",
        len(responses),
        uploaded_count,
    )
    return responses

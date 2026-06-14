import logging
import pandas as pd

from .__utils__ import (
    find_endpoint_response_files,
    load_endpoint_records,
    save_clean_dataframe,
)


logger = logging.getLogger(__name__)


LOCALITY_COLUMNS = [
    "loc_pid",
    "locality",
    "postcode",
    "state_name",
    "suburb_key",
    "lga_pid_ref",
]


def find_locality_response_files(data_dir="data", version="all", run_date=None):
    """Find locality response JSON files under the newest data date folder."""
    return find_endpoint_response_files(
        data_dir=data_dir,
        endpoint="locality",
        version=version,
        run_date=run_date,
    )


def load_localities_raw(data_dir="data", version="all", run_date=None):
    """Load raw locality records from response.json files."""
    logger.info(
        "Activity started | activity=load_localities_raw | data_dir=%s | version=%s | run_date=%s",
        data_dir,
        version,
        run_date,
    )
    return load_endpoint_records(
        data_dir=data_dir,
        endpoint="locality",
        version=version,
        run_date=run_date,
    )


def transform_localities(records):
    """Clean raw locality records and return a pandas DataFrame."""
    logger.info("Activity started | activity=transform_localities | input_records=%s", len(records))
    df = pd.DataFrame(records)

    if df.empty:
        logger.warning("No locality records available to transform")
        return pd.DataFrame(columns=LOCALITY_COLUMNS)

    for column in LOCALITY_COLUMNS:
        if column not in df.columns:
            logger.warning("Expected locality column missing; filling with NA | column=%s", column)
            df[column] = pd.NA

    df = df[LOCALITY_COLUMNS + [column for column in df.columns if column.startswith("_source_")]]

    string_columns = ["loc_pid", "locality", "postcode", "state_name", "suburb_key", "lga_pid_ref"]
    for column in string_columns:
        df[column] = df[column].astype("string").str.strip()

    df["loc_pid"] = df["loc_pid"].str.upper()
    df["locality"] = df["locality"].str.title()
    df["postcode"] = df["postcode"].str.extract(r"(\d{4})", expand=False)
    df["state_name"] = df["state_name"].str.upper()
    df["suburb_key"] = df["suburb_key"].str.lower()
    df["lga_pid_ref"] = df["lga_pid_ref"].str.upper()

    before_required_drop = len(df)
    df = df.dropna(subset=["loc_pid", "locality", "postcode", "state_name"])
    dropped_required = before_required_drop - len(df)
    if dropped_required:
        logger.warning("Dropped locality rows missing required values | rows=%s", dropped_required)

    duplicate_columns = ["loc_pid"]
    if "_source_file" in df.columns:
        duplicate_columns.append("_source_file")
    before_deduplicate = len(df)
    df = df.drop_duplicates(subset=duplicate_columns, keep="last").reset_index(drop=True)
    dropped_duplicates = before_deduplicate - len(df)
    if dropped_duplicates:
        logger.info("Dropped duplicate locality rows | rows=%s | subset=%s", dropped_duplicates, duplicate_columns)

    df = df.sort_values(["state_name", "locality", "postcode"], ignore_index=True)

    logger.info(
        "Activity completed | activity=transform_localities | input_records=%s | output_rows=%s",
        len(records),
        len(df),
    )
    return df


def load_transform_localities(data_dir="data", version="all", run_date=None):
    """Load localities from data/latest-date/locality and return a cleaned DataFrame."""
    logger.info("Activity started | activity=load_transform_localities")
    records = load_localities_raw(data_dir=data_dir, version=version, run_date=run_date)
    df = transform_localities(records)
    logger.info("Activity completed | activity=load_transform_localities | rows=%s", len(df))
    return df


def save_clean_localities(df, data_dir="data", run_date=None):
    """Overwrite the clean locality response file for the selected date."""
    output_path = save_clean_dataframe(
        df,
        data_dir=data_dir,
        endpoint="locality",
        run_date=run_date,
    )
    logger.info("Clean locality data saved | rows=%s | output_file=%s", len(df), output_path)
    return output_path


def load_transform_save_localities(data_dir="data", version="all", run_date=None):
    """Load raw localities, transform them, save clean output, and return the DataFrame."""
    logger.info("Activity started | activity=load_transform_save_localities")
    df = load_transform_localities(data_dir=data_dir, version=version, run_date=run_date)
    save_clean_localities(df, data_dir=data_dir, run_date=run_date)
    logger.info("Activity completed | activity=load_transform_save_localities | rows=%s", len(df))
    return df

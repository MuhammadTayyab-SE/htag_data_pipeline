import pandas as pd

from .__utils__ import (
    find_endpoint_response_files,
    load_endpoint_records,
    save_clean_dataframe,
)


LOCALITY_COLUMNS = [
    "loc_pid",
    "locality",
    "postcode",
    "state_name",
    "suburb_key",
    "lga_pid_ref",
]


def find_locality_response_files(data_dir="data", version="all"):
    """Find locality response JSON files under the newest data date folder."""
    return find_endpoint_response_files(data_dir=data_dir, endpoint="locality", version=version)


def load_localities_raw(data_dir="data", version="all"):
    """Load raw locality records from response.json files."""
    return load_endpoint_records(data_dir=data_dir, endpoint="locality", version=version)


def transform_localities(records):
    """Clean raw locality records and return a pandas DataFrame."""
    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=LOCALITY_COLUMNS)

    for column in LOCALITY_COLUMNS:
        if column not in df.columns:
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

    df = df.dropna(subset=["loc_pid", "locality", "postcode", "state_name"])
    duplicate_columns = ["loc_pid"]
    if "_source_file" in df.columns:
        duplicate_columns.append("_source_file")
    df = df.drop_duplicates(subset=duplicate_columns, keep="last").reset_index(drop=True)
    df = df.sort_values(["state_name", "locality", "postcode"], ignore_index=True)

    return df


def load_transform_localities(data_dir="data", version="all"):
    """Load localities from data/latest-date/locality and return a cleaned DataFrame."""
    records = load_localities_raw(data_dir=data_dir, version=version)
    return transform_localities(records)


def save_clean_localities(df, data_dir="data", run_date=None):
    """Overwrite the clean locality response file for the selected date."""
    return save_clean_dataframe(
        df,
        data_dir=data_dir,
        endpoint="locality",
        run_date=run_date,
    )


def load_transform_save_localities(data_dir="data", version="all", run_date=None):
    """Load raw localities, transform them, save clean output, and return the DataFrame."""
    df = load_transform_localities(data_dir=data_dir, version=version)
    save_clean_localities(df, data_dir=data_dir, run_date=run_date)
    return df

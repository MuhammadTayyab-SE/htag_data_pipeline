import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


LOCALITY_COLUMNS = [
    "loc_pid",
    "locality",
    "postcode",
    "state_name",
    "suburb_key",
    "lga_pid_ref",
]


def _parse_date_dir(name):
    for date_format in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(name, date_format).date()
        except ValueError:
            continue
    return None


def find_latest_date_dir(data_dir="data"):
    """Return the newest date folder inside the data directory."""
    data_path = Path(data_dir)
    dated_dirs = []

    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    for child in data_path.iterdir():
        parsed_date = _parse_date_dir(child.name)
        if child.is_dir() and parsed_date:
            dated_dirs.append((parsed_date, child))

    if not dated_dirs:
        raise FileNotFoundError(f"No date folders found in: {data_path}")

    return max(dated_dirs, key=lambda item: item[0])[1]


def _version_number(path):
    match = re.fullmatch(r"v(\d+)", path.name)
    return int(match.group(1)) if match else -1


def find_locality_response_files(data_dir="data", version="latest"):
    """
    Find locality response JSON files under the newest data date folder.

    version="latest" returns only the newest vNNN folder.
    version="all" returns every locality version for that date.
    """
    latest_date_dir = find_latest_date_dir(data_dir)
    locality_dir = latest_date_dir / "locality"

    if not locality_dir.exists():
        raise FileNotFoundError(f"Locality directory not found: {locality_dir}")

    version_dirs = [path for path in locality_dir.iterdir() if path.is_dir()]
    version_dirs = sorted(version_dirs, key=_version_number)

    if not version_dirs:
        raise FileNotFoundError(f"No locality version folders found in: {locality_dir}")

    if version == "latest":
        version_dirs = [version_dirs[-1]]
    elif version != "all":
        version_dirs = [locality_dir / version]

    files = [version_dir / "response.json" for version_dir in version_dirs]
    missing_files = [path for path in files if not path.exists()]
    if missing_files:
        missing = ", ".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"Missing locality response file(s): {missing}")

    return files


def load_localities_raw(data_dir="data", version="latest"):
    """Load raw locality records from response.json files."""
    records = []
    for file_path in find_locality_response_files(data_dir, version):
        with file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if isinstance(payload, dict):
            payload_records = payload.get("results", [])
        elif isinstance(payload, list):
            payload_records = payload
        else:
            payload_records = []

        for record in payload_records:
            record["_source_file"] = str(file_path)
            records.append(record)

    return records


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
    df = df.drop_duplicates(subset=["loc_pid","_source_file"], keep="last").reset_index(drop=True)
    df = df.sort_values(["state_name", "locality", "postcode"], ignore_index=True)

    return df


def load_transform_localities(data_dir="data", version="latest"):
    """Load localities from data/latest-date/locality and return a cleaned DataFrame."""
    records = load_localities_raw(data_dir=data_dir, version=version)
    return transform_localities(records)

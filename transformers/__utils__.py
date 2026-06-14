import json
import re
from datetime import datetime
from pathlib import Path


def parse_date_dir(name):
    """Parse supported data folder date formats."""
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
        parsed_date = parse_date_dir(child.name)
        if child.is_dir() and parsed_date:
            dated_dirs.append((parsed_date, child))

    if not dated_dirs:
        raise FileNotFoundError(f"No date folders found in: {data_path}")

    return max(dated_dirs, key=lambda item: item[0])[1]


def version_number(path):
    """Return numeric value for vNNN version folders."""
    match = re.fullmatch(r"v(\d+)", path.name)
    return int(match.group(1)) if match else -1


def find_endpoint_response_files(data_dir="data", endpoint="locality", version="latest"):
    """
    Find response JSON files under data/latest-date/endpoint.

    version="latest" returns only the newest vNNN folder.
    version="all" returns every endpoint version for that date.
    version="v001" returns that specific version folder.
    """
    latest_date_dir = find_latest_date_dir(data_dir)
    endpoint_dir = latest_date_dir / endpoint

    if not endpoint_dir.exists():
        raise FileNotFoundError(f"Endpoint directory not found: {endpoint_dir}")

    version_dirs = [path for path in endpoint_dir.iterdir() if path.is_dir()]
    version_dirs = sorted(version_dirs, key=version_number)

    if not version_dirs:
        raise FileNotFoundError(f"No version folders found in: {endpoint_dir}")

    if version == "latest":
        version_dirs = [version_dirs[-1]]
    elif version != "all":
        version_dirs = [endpoint_dir / version]

    files = [version_dir / "response.json" for version_dir in version_dirs]
    missing_files = [path for path in files if not path.exists()]
    if missing_files:
        missing = ", ".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"Missing response file(s): {missing}")

    return files


def records_from_payload(payload, records_key="results"):
    """Extract records from a common API JSON payload shape."""
    if isinstance(payload, dict):
        records = payload.get(records_key, [])
    elif isinstance(payload, list):
        records = payload
    else:
        records = []

    return records if isinstance(records, list) else []


def load_endpoint_records(data_dir="data", endpoint="locality", version="latest", records_key="results"):
    """Load records from endpoint response JSON files."""
    records = []
    for file_path in find_endpoint_response_files(data_dir, endpoint, version):
        with file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        for record in records_from_payload(payload, records_key):
            record = dict(record)
            record["_source_file"] = str(file_path)
            records.append(record)

    return records

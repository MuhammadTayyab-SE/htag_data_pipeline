import json
import logging
import re
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


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
        logger.error("Data directory not found | data_dir=%s", data_path)
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    for child in data_path.iterdir():
        parsed_date = parse_date_dir(child.name)
        if child.is_dir() and parsed_date:
            dated_dirs.append((parsed_date, child))

    if not dated_dirs:
        logger.error("No date folders found | data_dir=%s", data_path)
        raise FileNotFoundError(f"No date folders found in: {data_path}")

    latest_dir = max(dated_dirs, key=lambda item: item[0])[1]
    logger.info("Latest data directory selected | data_dir=%s", latest_dir)
    return latest_dir


def version_number(path):
    """Return numeric value for vNNN version folders."""
    match = re.fullmatch(r"v(\d+)", path.name)
    return int(match.group(1)) if match else -1


def _require_endpoint(endpoint):
    if not endpoint:
        raise ValueError("endpoint is required, for example endpoint='locality'")
    return endpoint


def find_endpoint_response_files(data_dir="data", endpoint=None, version="all", layer="raw", run_date=None):
    """
    Find response JSON files under data/latest-date/endpoint/layer.

    version="all" returns every endpoint version for that date.
    version="latest" returns only the newest vNNN folder.
    version="v001" returns that specific version folder.
    """
    endpoint = _require_endpoint(endpoint)
    if run_date:
        date_dir = Path(data_dir) / str(run_date)
    else:
        date_dir = find_latest_date_dir(data_dir)
    endpoint_dir = date_dir / endpoint / layer
    logger.info(
        "Activity started | activity=find_endpoint_response_files | endpoint=%s | version=%s | layer=%s | path=%s",
        endpoint,
        version,
        layer,
        endpoint_dir,
    )

    if not endpoint_dir.exists():
        logger.error("Endpoint directory not found | endpoint=%s | path=%s", endpoint, endpoint_dir)
        raise FileNotFoundError(f"Endpoint directory not found: {endpoint_dir}")

    version_dirs = [path for path in endpoint_dir.iterdir() if path.is_dir()]
    version_dirs = sorted(version_dirs, key=version_number)

    if not version_dirs:
        logger.error("No version folders found | endpoint=%s | path=%s", endpoint, endpoint_dir)
        raise FileNotFoundError(f"No version folders found in: {endpoint_dir}")

    if version == "latest":
        version_dirs = [version_dirs[-1]]
    elif version != "all":
        version_dirs = [endpoint_dir / version]

    files = [version_dir / "response.json" for version_dir in version_dirs]
    missing_files = [path for path in files if not path.exists()]
    if missing_files:
        missing = ", ".join(str(path) for path in missing_files)
        logger.error("Missing response files | endpoint=%s | missing=%s", endpoint, missing)
        raise FileNotFoundError(f"Missing response file(s): {missing}")

    logger.info(
        "Activity completed | activity=find_endpoint_response_files | endpoint=%s | files=%s",
        endpoint,
        len(files),
    )
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


def load_endpoint_records(
    data_dir="data",
    endpoint=None,
    version="all",
    records_key="results",
    layer="raw",
    run_date=None,
):
    """Load records from endpoint response JSON files."""
    endpoint = _require_endpoint(endpoint)

    logger.info(
        "Activity started | activity=load_endpoint_records | endpoint=%s | version=%s | layer=%s | run_date=%s",
        endpoint,
        version,
        layer,
        run_date,
    )
    records = []
    for file_path in find_endpoint_response_files(data_dir, endpoint, version, layer, run_date):
        logger.info("Reading endpoint response file | endpoint=%s | file=%s", endpoint, file_path)

        with file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        file_records = 0
        for record in records_from_payload(payload, records_key):
            record = dict(record)
            record["_source_file"] = str(file_path)
            records.append(record)
            file_records += 1
        logger.info("Loaded endpoint response file | endpoint=%s | file=%s | records=%s", endpoint, file_path, file_records)

    logger.info("Activity completed | activity=load_endpoint_records | endpoint=%s | total_records=%s", endpoint, len(records))
    return records


def clean_output_path(data_dir="data", endpoint=None, run_date=None, file_name="response.csv"):
    """Return data/date/endpoint/clean/file_name, creating the clean folder if needed."""
    endpoint = _require_endpoint(endpoint)
    if run_date:
        date_dir = Path(data_dir) / str(run_date)
    else:
        date_dir = find_latest_date_dir(data_dir)

    output_dir = date_dir / endpoint / "clean"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / file_name
    logger.info("Clean output path prepared | endpoint=%s | output_file=%s", endpoint, output_path)
    return output_path


def save_clean_dataframe(df, data_dir="data", endpoint=None, run_date=None, file_name="response.csv"):
    """
    Save a cleaned DataFrame to data/date/endpoint/clean/response.csv.

    This intentionally overwrites the clean file on each run.
    """
    output_path = clean_output_path(
        data_dir=data_dir,
        endpoint=endpoint,
        run_date=run_date,
        file_name=file_name,
    )
    logger.info("Activity started | activity=save_clean_dataframe | endpoint=%s | rows=%s | output_file=%s", endpoint, len(df), output_path)
    df.to_csv(output_path, index=False)
    logger.info("Activity completed | activity=save_clean_dataframe | endpoint=%s | rows=%s | output_file=%s", endpoint, len(df), output_path)
    return output_path

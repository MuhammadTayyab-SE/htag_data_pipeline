import json
import logging
import re
from datetime import date
from pathlib import Path


logger = logging.getLogger(__name__)


def endpoint_to_folder(endpoint_path):
    """Convert an API path into a filesystem-safe folder name."""
    cleaned = endpoint_path.strip("/")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", cleaned).strip("_").lower()
    return slug or "root"


def next_version_folder(endpoint_dir):
    existing_versions = []
    if endpoint_dir.exists():
        for child in endpoint_dir.iterdir():
            if child.is_dir() and re.fullmatch(r"v\d+", child.name):
                existing_versions.append(int(child.name[1:]))

    next_version = max(existing_versions, default=0) + 1
    return endpoint_dir / f"v{next_version:03d}"


def save_json_response(response_data, endpoint_path, base_dir="data", run_date=None):
    """
    Save an API response under data/YYYYMMDD/endpoint/raw/vNNN/response.json.

    Returns the path to the written JSON file.
    """
    run_date = run_date or date.today().strftime("%Y%m%d")
    endpoint_folder = endpoint_to_folder(endpoint_path)
    endpoint_dir = Path(base_dir) / run_date / endpoint_folder / "raw/"
    logger.info(
        "Activity started | activity=save_json_response | endpoint=%s | base_dir=%s | run_date=%s",
        endpoint_path,
        base_dir,
        run_date,
    )
    version_dir = next_version_folder(endpoint_dir)
    version_dir.mkdir(parents=True, exist_ok=False)

    output_path = version_dir / "response.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(response_data, file, indent=2, ensure_ascii=False)
        file.write("\n")

    record_count = len(response_data.get("results", [])) if isinstance(response_data, dict) else None
    logger.info(
        "Activity completed | activity=save_json_response | endpoint=%s | records=%s | output_file=%s",
        endpoint_path,
        record_count,
        output_path,
    )
    return output_path

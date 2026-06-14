import logging
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.endpoints import ENDPOINTS
from htag_data_pipeline.htag_client import fetch_endpoint_data, fetch_localities
from htag_data_pipeline.json_storage import save_json_response


def ingest_localities_pipeline(data_dir="data", run_date=None):
    """Fetch localities from HTAG API and save raw JSON locally."""
    try:
        localities = fetch_localities()
        payload = {"results": localities, "total": len(localities)}
        output_file = save_json_response(
            response_data=payload,
            endpoint_path="locality",
            base_dir=data_dir,
            run_date=run_date,
        )
        return True
    except:
        return False

def ingest_endpoint_pipeline(endpoint_path, localities, data_dir="data", run_date=None, sleep_seconds=0.3):
    """Fetch one HTAG endpoint for each locality and save raw JSON locally."""
    records = []

    for locality in localities:
        loc_pid = locality["loc_pid"]
        data = fetch_endpoint_data(endpoint_path, loc_pid)
        if data:
            data["loc_pid"] = loc_pid
            records.append(data)
        else:
            logging.warning("Failed: %s for %s", endpoint_path, loc_pid)
        time.sleep(sleep_seconds)

    payload = {"results": records, "total": len(records)}
    output_file = save_json_response(
        payload,
        endpoint_path,
        base_dir=data_dir,
        run_date=run_date,
    )
    return output_file


def ingest_all_pipeline(data_dir="data", run_date=None, endpoints=None, sleep_seconds=0.3):
    """Fetch localities and configured HTAG endpoints, saving raw JSON files locally."""
    outputs = {}

    localities = fetch_localities()
    locality_payload = {"results": localities, "total": len(localities)}
    outputs["locality"] = save_json_response(
        locality_payload,
        "locality",
        base_dir=data_dir,
        run_date=run_date,
    )

    for endpoint in endpoints or ENDPOINTS:
        outputs[endpoint["path"]] = ingest_endpoint_pipeline(
            endpoint_path=endpoint["path"],
            localities=localities,
            data_dir=data_dir,
            run_date=run_date,
            sleep_seconds=sleep_seconds,
        )

    return outputs


if __name__ == "__main__":
    ingest_all_pipeline()

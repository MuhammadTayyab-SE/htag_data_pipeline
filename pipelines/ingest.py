import logging
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.endpoints import ENDPOINTS
from htag_data_pipeline.htag_client import fetch_endpoint_data, fetch_localities
from htag_data_pipeline.json_storage import save_json_response


logger = logging.getLogger(__name__)


def ingest_localities_pipeline(data_dir="data", run_date=None):
    """Fetch localities from HTAG API and save raw JSON locally."""
    logger.info("Activity started | activity=fetch_and_save_localities | data_dir=%s | run_date=%s", data_dir, run_date)
    try:
        localities = fetch_localities()
        payload = {"results": localities, "total": len(localities)}
        output_file = save_json_response(
            response_data=payload,
            endpoint_path="locality",
            base_dir=data_dir,
            run_date=run_date,
        )
        logger.info(
            "Activity completed | activity=fetch_and_save_localities | records=%s | output_file=%s",
            len(localities),
            output_file,
        )
        return True
    except Exception:
        logger.exception("Activity failed | activity=fetch_and_save_localities")
        return False

def ingest_endpoint_pipeline(endpoint_path, localities, data_dir="data", run_date=None, sleep_seconds=0.3):
    """Fetch one HTAG endpoint for each locality and save raw JSON locally."""
    logger.info(
        "Activity started | activity=fetch_endpoint_for_localities | endpoint=%s | localities=%s | data_dir=%s | run_date=%s",
        endpoint_path,
        len(localities),
        data_dir,
        run_date,
    )
    records = []

    for locality in localities:
        loc_pid = locality["loc_pid"]
        data = fetch_endpoint_data(endpoint_path, loc_pid)
        if data:
            data["loc_pid"] = loc_pid
            records.append(data)
        else:
            logger.warning("Endpoint fetch returned no data | endpoint=%s | loc_pid=%s", endpoint_path, loc_pid)
        time.sleep(sleep_seconds)

    payload = {"results": records, "total": len(records)}
    output_file = save_json_response(
        payload,
        endpoint_path,
        base_dir=data_dir,
        run_date=run_date,
    )
    logger.info(
        "Activity completed | activity=fetch_endpoint_for_localities | endpoint=%s | records=%s | output_file=%s",
        endpoint_path,
        len(records),
        output_file,
    )
    return output_file


def ingest_all_pipeline(data_dir="data", run_date=None, endpoints=None, sleep_seconds=0.3):
    """Fetch localities and configured HTAG endpoints, saving raw JSON files locally."""
    logger.info("Pipeline started | pipeline=ingest_all | data_dir=%s | run_date=%s", data_dir, run_date)
    outputs = {}

    localities = fetch_localities()
    logger.info("Fetched localities for ingest_all | records=%s", len(localities))
    locality_payload = {"results": localities, "total": len(localities)}
    outputs["locality"] = save_json_response(
        locality_payload,
        "locality",
        base_dir=data_dir,
        run_date=run_date,
    )
    logger.info("Saved locality response | output_file=%s", outputs["locality"])

    for endpoint in endpoints or ENDPOINTS:
        logger.info("Endpoint ingest started | endpoint=%s", endpoint["path"])
        outputs[endpoint["path"]] = ingest_endpoint_pipeline(
            endpoint_path=endpoint["path"],
            localities=localities,
            data_dir=data_dir,
            run_date=run_date,
            sleep_seconds=sleep_seconds,
        )
        logger.info("Endpoint ingest completed | endpoint=%s | output_file=%s", endpoint["path"], outputs[endpoint["path"]])

    logger.info("Pipeline completed | pipeline=ingest_all | outputs=%s", len(outputs))
    return outputs


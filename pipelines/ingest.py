import csv
import logging
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.endpoints import ENDPOINTS
from htag_data_pipeline.htag_client import fetch_endpoint_data, fetch_localities, get_endpoint_config
from htag_data_pipeline.json_storage import save_json_response
from htag_data_pipeline.pipeline_config import enabled_endpoints_for_step, load_pipeline_config


logger = logging.getLogger(__name__)


def console_action(message):
    print(message, flush=True)


def load_clean_localities_for_ingest(data_dir="data", run_date=None, limit=3000):
    """Load cleaned localities from data/YYYYMMDD/locality/clean/response.csv."""
    if run_date is None:
        from htag_data_pipeline.transformers.__utils__ import find_latest_date_dir

        date_dir = find_latest_date_dir(data_dir)
    else:
        date_dir = Path(data_dir) / str(run_date)

    file_path = date_dir / "locality" / "clean" / "response.csv"
    logger.info("Activity started | activity=load_clean_localities_for_ingest | file=%s | limit=%s", file_path, limit)
    if not file_path.exists():
        logger.error("Clean locality CSV file not found | file=%s", file_path)
        raise FileNotFoundError(f"Clean locality CSV file not found: {file_path}")

    localities = []
    with file_path.open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            localities.append(row)
            if limit and len(localities) >= limit:
                break

    logger.info(
        "Activity completed | activity=load_clean_localities_for_ingest | records=%s | file=%s",
        len(localities),
        file_path,
    )
    return localities


def chunked(values, size):
    for index in range(0, len(values), size):
        yield values[index:index + size]


def locality_area_id(locality):
    return locality.get("loc_pid") or locality.get("area_id")


def append_endpoint_response(records, data):
    if not data:
        return 0

    if isinstance(data, dict) and isinstance(data.get("results"), list):
        records.extend(data["results"])
        return len(data["results"])

    records.append(data)
    return 1


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

    # reading configurations for endpoints
    endpoint_config = get_endpoint_config(endpoint_path)

    resolved_endpoint_path = endpoint_config["path"]
    endpoint_params = endpoint_config.get("params") or {}
    uses_area_id_batches = "area_id" in endpoint_params
    batch_size = int(endpoint_config.get("batch_size", 500))

    logger.info(
        "Activity started | activity=fetch_endpoint_for_localities | endpoint=%s | localities=%s | batch_mode=%s | data_dir=%s | run_date=%s",
        resolved_endpoint_path,
        len(localities),
        uses_area_id_batches,
        data_dir,
        run_date,
    )
    console_action(f"Endpoint started | {resolved_endpoint_path} | localities={len(localities)}")
    records = []

    # if batching is enabled 
    if uses_area_id_batches:
        area_ids = [area_id for area_id in (locality_area_id(locality) for locality in localities) if area_id]
        for batch_number, area_id_batch in enumerate(chunked(area_ids, batch_size), start=1):
            data = fetch_endpoint_data(endpoint_path, extra_params={"area_id": area_id_batch})
            appended_records = append_endpoint_response(records, data)
            if appended_records:
                logger.info(
                    "Endpoint batch fetched | endpoint=%s | batch=%s | area_ids=%s | records=%s",
                    resolved_endpoint_path,
                    batch_number,
                    len(area_id_batch),
                    appended_records,
                )
            else:
                logger.warning(
                    "Endpoint batch returned no data | endpoint=%s | batch=%s | area_ids=%s",
                    resolved_endpoint_path,
                    batch_number,
                    len(area_id_batch),
                )
            time.sleep(sleep_seconds)
    else:
        # execute locality by locality 
        for locality in localities:
            loc_pid = locality["loc_pid"]
            data = fetch_endpoint_data(endpoint_path, loc_pid)
            if data:
                data["loc_pid"] = loc_pid
                records.append(data)
            else:
                logger.warning("Endpoint fetch returned no data | endpoint=%s | loc_pid=%s", resolved_endpoint_path, loc_pid)
            time.sleep(sleep_seconds)

    payload = {"results": records, "total": len(records)}
    output_file = save_json_response(
        payload,
        resolved_endpoint_path,
        base_dir=data_dir,
        run_date=run_date,
    )
    logger.info(
        "Activity completed | activity=fetch_endpoint_for_localities | endpoint=%s | records=%s | output_file=%s",
        resolved_endpoint_path,
        len(records),
        output_file,
    )
    console_action(f"Endpoint finished | {resolved_endpoint_path} | records={len(records)}")
    return output_file


def ingest_all_pipeline(
    data_dir="data",
    run_date=None,
    endpoints=None,
    sleep_seconds=0.3,
    pipeline_config=None,
    locality_limit=3000,
):
    """Fetch configured HTAG endpoints using cleaned localities from disk."""

    logger.info("Pipeline started | pipeline=ingest_all | data_dir=%s | run_date=%s", data_dir, run_date)
    console_action(f"Pipeline started | ingest_all | run_date={run_date}")

    outputs = {}
    pipeline_config = pipeline_config or load_pipeline_config()

    localities = load_clean_localities_for_ingest(
        data_dir=data_dir,
        run_date=run_date,
        limit=locality_limit,
    )
    logger.info("Loaded clean localities for endpoint ingest | records=%s", len(localities))
    console_action(f"Loaded clean localities | records={len(localities)}")

    for endpoint in enabled_endpoints_for_step(pipeline_config, "ingest", endpoints or ENDPOINTS):
        endpoint_config = get_endpoint_config(endpoint)
        endpoint_path = endpoint_config["path"]

        logger.info("Endpoint ingest started | endpoint=%s", endpoint_path)
        outputs[endpoint_path] = ingest_endpoint_pipeline(
            endpoint_path=endpoint,
            localities=localities,
            data_dir=data_dir,
            run_date=run_date,
            sleep_seconds=sleep_seconds,
        )
        logger.info("Endpoint ingest completed | endpoint=%s | output_file=%s", endpoint_path, outputs[endpoint_path])
        console_action(f"Endpoint ingest completed | {endpoint_path} | output={outputs[endpoint_path]}")

    logger.info("Pipeline completed | pipeline=ingest_all | outputs=%s", len(outputs))
    console_action(f"Pipeline finished | ingest_all | outputs={len(outputs)}")
    return outputs

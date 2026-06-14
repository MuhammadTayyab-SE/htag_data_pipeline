import logging
import requests
import time
from htag_data_pipeline.config import HTAG_BASE_URL, HTAG_HEADERS


logger = logging.getLogger(__name__)


def fetch_localities(limit=1000):
    """Fetch all suburbs (LOC_PIDs) with pagination"""
    logger.info("Activity started | activity=fetch_localities | limit=%s", limit)
    all_localities = []
    offset = 0
    while True:
        params = {"limit": limit, "offset": offset}
        logger.info("Request started | endpoint=/reference/locality | offset=%s | limit=%s", offset, limit)
        resp = requests.get(f"{HTAG_BASE_URL}/reference/locality", headers=HTAG_HEADERS, params=params, timeout=30)
        logger.info(
            "Request completed | endpoint=/reference/locality | offset=%s | status_code=%s",
            offset,
            resp.status_code,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            logger.info("No more locality records returned | offset=%s", offset)
            break
        all_localities.extend(results)
        logger.info("Locality page fetched | offset=%s | page_records=%s | total_records=%s", offset, len(results), len(all_localities))
        offset += limit
        time.sleep(0.5)  # rate limiting
    logger.info("Activity completed | activity=fetch_localities | total_records=%s", len(all_localities))
    return all_localities

def fetch_endpoint_data(endpoint_path, loc_pid):
    """Fetch data for a single suburb from a single endpoint"""
    url = f"{HTAG_BASE_URL}{endpoint_path}"
    params = {"loc_pid": loc_pid}
    logger.info("Request started | endpoint=%s | loc_pid=%s", endpoint_path, loc_pid)
    resp = requests.get(url, headers=HTAG_HEADERS, params=params, timeout=30)
    if resp.status_code == 200:
        logger.info("Request completed | endpoint=%s | loc_pid=%s | status_code=%s", endpoint_path, loc_pid, resp.status_code)
        return resp.json()
    else:
        logger.warning("Request failed | endpoint=%s | loc_pid=%s | status_code=%s | response=%s", endpoint_path, loc_pid, resp.status_code, resp.text[:500])
        return None

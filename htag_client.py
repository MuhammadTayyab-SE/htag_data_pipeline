import logging
import requests
import time
from htag_data_pipeline.config import HTAG_BASE_URL, HTAG_HEADERS
from htag_data_pipeline.endpoints import ENDPOINTS


logger = logging.getLogger(__name__)


def get_endpoint_config(endpoint):
    """Return endpoint metadata from ENDPOINTS for a path or endpoint dict."""
    if isinstance(endpoint, dict):
        return endpoint

    for endpoint_config in ENDPOINTS:
        if endpoint_config.get("path") == endpoint:
            return endpoint_config

    return {"path": endpoint}


def build_endpoint_params(endpoint_config, loc_pid=None, extra_params=None):
    """Build request params from endpoint metadata plus per-call values."""
    params = {}
    for key, value in (endpoint_config.get("params") or {}).items():
        params[key] = list(value) if isinstance(value, list) else value

    if loc_pid is not None and "area_id" not in params:
        params["loc_pid"] = loc_pid

    if extra_params:
        params.update(extra_params)

    return params


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

def fetch_endpoint_data(endpoint, loc_pid=None, extra_params=None):
    """Fetch all available pages from a configured endpoint."""
    endpoint_config = get_endpoint_config(endpoint)
    endpoint_path = endpoint_config["path"]
    url = f"{HTAG_BASE_URL}{endpoint_path}"
    params = build_endpoint_params(endpoint_config, loc_pid=loc_pid, extra_params=extra_params)
    timeout = endpoint_config.get("timeout", 30)
    limit = int(params.get("limit", 1000))
    offset = int(params.get("offset", 0))
    all_results = []
    response_payload = None

    while True:
        params["limit"] = limit
        params["offset"] = offset

        logger.info("Request started | endpoint=%s | loc_pid=%s | params=%s", endpoint_path, loc_pid, params)
        resp = requests.get(url, headers=HTAG_HEADERS, params=params, timeout=timeout)
        if resp.status_code != 200:
            logger.warning("Request failed | endpoint=%s | loc_pid=%s | status_code=%s | response=%s", endpoint_path, loc_pid, resp.status_code, resp.text[:500])
            return None

        response_payload = resp.json()
        page_results = response_payload.get("results", []) if isinstance(response_payload, dict) else []
        logger.info(
            "Request completed | endpoint=%s | loc_pid=%s | offset=%s | limit=%s | page_records=%s | status_code=%s",
            endpoint_path,
            loc_pid,
            offset,
            limit,
            len(page_results),
            resp.status_code,
        )

        if not page_results:
            break

        all_results.extend(page_results)
        if len(page_results) < limit:
            break

        offset += limit
        time.sleep(endpoint_config.get("pagination_sleep_seconds", 0.2))

    if isinstance(response_payload, dict):
        response_payload["results"] = all_results
        response_payload["total"] = len(all_results)
        return response_payload

    return {"results": all_results, "total": len(all_results)}

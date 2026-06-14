import requests
import time
from config import HTAG_BASE_URL, HTAG_HEADERS
print(HTAG_BASE_URL, HTAG_HEADERS)

def fetch_localities(limit=1000):
    """Fetch all suburbs (LOC_PIDs) with pagination"""
    all_localities = []
    offset = 0
    while True:
        params = {"limit": limit, "offset": offset}
        resp = requests.get(f"{HTAG_BASE_URL}/reference/locality", headers=HTAG_HEADERS, params=params, timeout=30)
        data = resp.json()
        print(resp.json())
        results = data.get("results", [])
        if not results:
            break
        all_localities.extend(results)
        offset += limit
        time.sleep(0.5)  # rate limiting
    return all_localities

def fetch_endpoint_data(endpoint_path, loc_pid):
    """Fetch data for a single suburb from a single endpoint"""
    url = f"{HTAG_BASE_URL}{endpoint_path}"
    params = {"loc_pid": loc_pid}
    resp = requests.get(url, headers=HTAG_HEADERS, params=params, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None
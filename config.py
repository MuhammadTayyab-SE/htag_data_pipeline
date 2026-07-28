import os
from dotenv import load_dotenv

load_dotenv()

HTAG_API_KEY = os.getenv("HTAG_API_KEY")
HTAG_BASE_URL = "https://api.htagai.com/v1"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SCHEMA = "htag"

HTAG_HEADERS = {
    "x-api-key": HTAG_API_KEY,
    "Accept": "application/json"
}

ENDPOINT_TABLE_MAP = {
    "locality": "localities",
}

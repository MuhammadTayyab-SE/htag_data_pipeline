from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_YIELD_ENDPOINT = "/markets/trends/yield"
MARKET_TRENDS_YIELD_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "yield",
]


def transform_market_trends_yield(records):
    """Clean raw market_trends_yield records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_TRENDS_YIELD_ENDPOINT, MARKET_TRENDS_YIELD_COLUMNS)


def load_transform_market_trends_yield(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_yield data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_YIELD_ENDPOINT,
        MARKET_TRENDS_YIELD_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_yield(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_yield records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_YIELD_ENDPOINT,
        MARKET_TRENDS_YIELD_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_PRICE_ENDPOINT = "/markets/trends/price"
MARKET_TRENDS_PRICE_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "typical_price",
    "sales",
]


def transform_market_trends_price(records):
    """Clean raw market_trends_price records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_TRENDS_PRICE_ENDPOINT, MARKET_TRENDS_PRICE_COLUMNS)


def load_transform_market_trends_price(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_price data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_PRICE_ENDPOINT,
        MARKET_TRENDS_PRICE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_price(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_price records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_PRICE_ENDPOINT,
        MARKET_TRENDS_PRICE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
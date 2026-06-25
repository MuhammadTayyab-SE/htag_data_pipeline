from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_RENT_ENDPOINT = "/markets/trends/rent"
MARKET_TRENDS_RENT_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "median_rent",
    "rentals",
]


def transform_market_trends_rent(records):
    """Clean raw market_trends_rent records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_TRENDS_RENT_ENDPOINT, MARKET_TRENDS_RENT_COLUMNS)


def load_transform_market_trends_rent(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_rent data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_RENT_ENDPOINT,
        MARKET_TRENDS_RENT_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_rent(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_rent records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_RENT_ENDPOINT,
        MARKET_TRENDS_RENT_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
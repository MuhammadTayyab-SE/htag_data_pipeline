from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_DAYS_ON_MARKET_ENDPOINT = "/markets/trends/days-on-market"
MARKET_TRENDS_DAYS_ON_MARKET_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "dom",
    "discounting",
]


def transform_market_trends_days_on_market(records):
    """Clean raw market_trends_days_on_market records and return a pandas DataFrame."""
    return transform_market_endpoint_records(
        records,
        MARKET_TRENDS_DAYS_ON_MARKET_ENDPOINT,
        MARKET_TRENDS_DAYS_ON_MARKET_COLUMNS,
    )


def load_transform_market_trends_days_on_market(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_days_on_market data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_DAYS_ON_MARKET_ENDPOINT,
        MARKET_TRENDS_DAYS_ON_MARKET_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_days_on_market(data_dir="data", version="all", run_date=None):
    """Load, transform, and save clean market_trends_days_on_market data."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_DAYS_ON_MARKET_ENDPOINT,
        MARKET_TRENDS_DAYS_ON_MARKET_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )

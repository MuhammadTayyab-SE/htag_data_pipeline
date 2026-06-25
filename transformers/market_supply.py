from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_SUPPLY_ENDPOINT = "/markets/supply"
MARKET_SUPPLY_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "som_percent",
    "inventory",
    "building_approvals_estimated",
    "ba_ratio",
    "hold_period",
]


def transform_market_supply(records):
    """Clean raw market_supply records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_SUPPLY_ENDPOINT, MARKET_SUPPLY_COLUMNS)


def load_transform_market_supply(data_dir="data", version="all", run_date=None):
    """Load raw market_supply data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_SUPPLY_ENDPOINT,
        MARKET_SUPPLY_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_supply(data_dir="data", version="all", run_date=None):
    """Load raw market_supply records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_SUPPLY_ENDPOINT,
        MARKET_SUPPLY_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
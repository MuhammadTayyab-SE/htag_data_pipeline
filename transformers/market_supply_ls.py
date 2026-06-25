from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_SUPPLY_LS_ENDPOINT = "/markets/supply/ls"
MARKET_SUPPLY_LS_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "ls_som_perc",
    "ls_inventory",
    "ls_hold_period",
]


def transform_market_supply_ls(records):
    """Clean raw market_supply_ls records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_SUPPLY_LS_ENDPOINT, MARKET_SUPPLY_LS_COLUMNS)


def load_transform_market_supply_ls(data_dir="data", version="all", run_date=None):
    """Load raw market_supply_ls data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_SUPPLY_LS_ENDPOINT,
        MARKET_SUPPLY_LS_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_supply_ls(data_dir="data", version="all", run_date=None):
    """Load raw market_supply_ls records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_SUPPLY_LS_ENDPOINT,
        MARKET_SUPPLY_LS_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
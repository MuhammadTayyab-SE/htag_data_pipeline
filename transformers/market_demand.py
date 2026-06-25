from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_DEMAND_ENDPOINT = "/markets/demand"
MARKET_DEMAND_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "dom",
    "discounting",
    "vacancy_rate",
    "vacancies",
    "dorm",
    "clearance_rate",
    "auctions",
    "buy_si",
    "rent_si",
]


def transform_market_demand(records):
    """Clean raw market_demand records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_DEMAND_ENDPOINT, MARKET_DEMAND_COLUMNS)


def load_transform_market_demand(data_dir="data", version="all", run_date=None):
    """Load raw market_demand data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_DEMAND_ENDPOINT,
        MARKET_DEMAND_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_demand(data_dir="data", version="all", run_date=None):
    """Load raw market_demand records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_DEMAND_ENDPOINT,
        MARKET_DEMAND_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
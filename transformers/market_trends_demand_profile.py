from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_DEMAND_PROFILE_ENDPOINT = "/markets/trends/demand-profile"
MARKET_TRENDS_DEMAND_PROFILE_COLUMNS = [
    "area_id",
    "period_end",
    "dwelling_type",
    "bedrooms",
    "sales",
]


def transform_market_trends_demand_profile(records):
    """Clean raw market_trends_demand_profile records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_TRENDS_DEMAND_PROFILE_ENDPOINT, MARKET_TRENDS_DEMAND_PROFILE_COLUMNS)


def load_transform_market_trends_demand_profile(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_demand_profile data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_DEMAND_PROFILE_ENDPOINT,
        MARKET_TRENDS_DEMAND_PROFILE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_demand_profile(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_demand_profile records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_DEMAND_PROFILE_ENDPOINT,
        MARKET_TRENDS_DEMAND_PROFILE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
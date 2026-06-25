from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_CYCLE_ENDPOINT = "/markets/cycle"
MARKET_CYCLE_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "growth_rate_cycle",
    "grc_price_index",
    "min_grc",
    "gpd_3",
    "gpd_5",
    "gpd_10",
    "gsp_3",
    "gsp_5",
    "gsp_10",
    "projected_annual_capital_growth_low",
    "projected_annual_capital_growth_high",
    "projected_annual_rent_increase",
    "projected_annual_roi_low",
    "projected_annual_roi_high",
]


def transform_market_cycle(records):
    """Clean raw market_cycle records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_CYCLE_ENDPOINT, MARKET_CYCLE_COLUMNS)


def load_transform_market_cycle(data_dir="data", version="all", run_date=None):
    """Load raw market_cycle data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_CYCLE_ENDPOINT,
        MARKET_CYCLE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_cycle(data_dir="data", version="all", run_date=None):
    """Load raw market_cycle records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_CYCLE_ENDPOINT,
        MARKET_CYCLE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
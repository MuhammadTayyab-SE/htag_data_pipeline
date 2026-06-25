from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_RISK_ENDPOINT = "/markets/risk"
MARKET_RISK_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "hrp_flood",
    "hrp_fire",
    "ediv_ind",
    "madi",
    "gpo_dist",
]


def transform_market_risk(records):
    """Clean raw market_risk records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_RISK_ENDPOINT, MARKET_RISK_COLUMNS)


def load_transform_market_risk(data_dir="data", version="all", run_date=None):
    """Load raw market_risk data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_RISK_ENDPOINT,
        MARKET_RISK_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_risk(data_dir="data", version="all", run_date=None):
    """Load raw market_risk records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_RISK_ENDPOINT,
        MARKET_RISK_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
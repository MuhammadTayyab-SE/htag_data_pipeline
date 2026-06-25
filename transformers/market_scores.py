from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_SCORES_ENDPOINT = "/markets/scores"
MARKET_SCORES_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "rcs_lower_risk",
    "rcs_cashflow",
    "rcs_capital_growth",
    "rcs_overall",
    "hapi_score",
    "volatility_index",
]


def transform_market_scores(records):
    """Clean raw market_scores records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_SCORES_ENDPOINT, MARKET_SCORES_COLUMNS)


def load_transform_market_scores(data_dir="data", version="all", run_date=None):
    """Load raw market_scores data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_SCORES_ENDPOINT,
        MARKET_SCORES_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_scores(data_dir="data", version="all", run_date=None):
    """Load raw market_scores records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_SCORES_ENDPOINT,
        MARKET_SCORES_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
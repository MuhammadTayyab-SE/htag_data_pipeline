from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_YEARS_TO_OWN_ENDPOINT = "/markets/trends/years-to-own"
MARKET_TRENDS_YEARS_TO_OWN_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "years_to_own",
]


def transform_market_trends_years_to_own(records):
    """Clean raw market_trends_years_to_own records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_TRENDS_YEARS_TO_OWN_ENDPOINT, MARKET_TRENDS_YEARS_TO_OWN_COLUMNS)


def load_transform_market_trends_years_to_own(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_years_to_own data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_YEARS_TO_OWN_ENDPOINT,
        MARKET_TRENDS_YEARS_TO_OWN_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_years_to_own(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_years_to_own records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_YEARS_TO_OWN_ENDPOINT,
        MARKET_TRENDS_YEARS_TO_OWN_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_FUNDAMENTALS_ENDPOINT = "/markets/fundamentals"
MARKET_FUNDAMENTALS_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "irsad",
    "ro_ratio",
    "uh_ratio",
    "uhv_ratio",
    "years_to_own",
    "non_res_ba_per_capita_value",
]


def transform_market_fundamentals(records):
    """Clean raw market_fundamentals records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_FUNDAMENTALS_ENDPOINT, MARKET_FUNDAMENTALS_COLUMNS)


def load_transform_market_fundamentals(data_dir="data", version="all", run_date=None):
    """Load raw market_fundamentals data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_FUNDAMENTALS_ENDPOINT,
        MARKET_FUNDAMENTALS_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_fundamentals(data_dir="data", version="all", run_date=None):
    """Load raw market_fundamentals records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_FUNDAMENTALS_ENDPOINT,
        MARKET_FUNDAMENTALS_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
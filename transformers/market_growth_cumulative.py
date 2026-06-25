from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_GROWTH_CUMULATIVE_ENDPOINT = "/markets/growth/cumulative"
MARKET_GROWTH_CUMULATIVE_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "price_1m_growth",
    "price_1q_growth",
    "price_6m_growth",
    "price_1y_growth",
    "price_3y_growth",
    "price_5y_growth",
    "price_10y_growth",
    "rent_1m_growth",
    "rent_1q_growth",
    "rent_6m_growth",
    "rent_1y_growth",
    "rent_3y_growth",
    "rent_5y_growth",
    "rent_10y_growth",
    "yield_1m_growth",
    "yield_1q_growth",
    "yield_6m_growth",
    "yield_1y_growth",
    "yield_3y_growth",
    "yield_5y_growth",
    "yield_10y_growth",
]


def transform_market_growth_cumulative(records):
    """Clean raw market_growth_cumulative records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_GROWTH_CUMULATIVE_ENDPOINT, MARKET_GROWTH_CUMULATIVE_COLUMNS)


def load_transform_market_growth_cumulative(data_dir="data", version="all", run_date=None):
    """Load raw market_growth_cumulative data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_GROWTH_CUMULATIVE_ENDPOINT,
        MARKET_GROWTH_CUMULATIVE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_growth_cumulative(data_dir="data", version="all", run_date=None):
    """Load raw market_growth_cumulative records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_GROWTH_CUMULATIVE_ENDPOINT,
        MARKET_GROWTH_CUMULATIVE_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
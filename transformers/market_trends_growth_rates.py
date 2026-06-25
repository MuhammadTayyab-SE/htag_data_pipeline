from .market_endpoints import (
    load_transform_market_endpoint,
    load_transform_save_market_endpoint,
    transform_market_endpoint_records,
)


MARKET_TRENDS_GROWTH_RATES_ENDPOINT = "/markets/trends/growth-rates"
MARKET_TRENDS_GROWTH_RATES_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "price_chg",
    "sales_chg",
    "rent_chg",
    "rentals_chg",
    "buy_si_chg",
    "rent_si_chg",
    "yield_chg",
]


def transform_market_trends_growth_rates(records):
    """Clean raw market_trends_growth_rates records and return a pandas DataFrame."""
    return transform_market_endpoint_records(records, MARKET_TRENDS_GROWTH_RATES_ENDPOINT, MARKET_TRENDS_GROWTH_RATES_COLUMNS)


def load_transform_market_trends_growth_rates(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_growth_rates data and return a cleaned DataFrame."""
    return load_transform_market_endpoint(
        MARKET_TRENDS_GROWTH_RATES_ENDPOINT,
        MARKET_TRENDS_GROWTH_RATES_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )


def load_transform_save_market_trends_growth_rates(data_dir="data", version="all", run_date=None):
    """Load raw market_trends_growth_rates records, transform them, save clean output, and return the DataFrame."""
    return load_transform_save_market_endpoint(
        MARKET_TRENDS_GROWTH_RATES_ENDPOINT,
        MARKET_TRENDS_GROWTH_RATES_COLUMNS,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
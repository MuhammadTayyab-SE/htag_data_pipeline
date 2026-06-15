import logging
import pandas as pd

from .__utils__ import (
    load_endpoint_records,
    save_clean_dataframe,
)


logger = logging.getLogger(__name__)


MARKETS_TRENDS_PRICE_ENDPOINT = "markets_trends_price"
MARKETS_TRENDS_PRICE_COLUMNS = [
    "area_id",
    "period_end",
    "property_type",
    "bedrooms",
    "typical_price",
    "sales",
]


def transform_markets_trends_price(records):
    """Clean raw markets trends price records and return a pandas DataFrame."""
    logger.info("Activity started | activity=transform_markets_trends_price | input_records=%s", len(records))
    df = pd.DataFrame(records)

    if df.empty:
        logger.warning("No markets trends price records available to transform")
        return pd.DataFrame(columns=MARKETS_TRENDS_PRICE_COLUMNS)

    for column in MARKETS_TRENDS_PRICE_COLUMNS:
        if column not in df.columns:
            logger.warning("Expected markets trends price column missing; filling with NA | column=%s", column)
            df[column] = pd.NA

    source_columns = [column for column in df.columns if column.startswith("_source_")]
    df = df[MARKETS_TRENDS_PRICE_COLUMNS + source_columns]

    string_columns = ["area_id", "property_type", "bedrooms"]
    for column in string_columns:
        df[column] = df[column].astype("string").str.strip()

    df["area_id"] = df["area_id"].str.upper()
    df["property_type"] = df["property_type"].str.lower()
    df["bedrooms"] = df["bedrooms"].str.strip()
    df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce", utc=True).dt.date
    df["typical_price"] = pd.to_numeric(df["typical_price"], errors="coerce").astype("Int64")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce").astype("Int64")

    before_required_drop = len(df)
    df = df.dropna(subset=["area_id", "period_end", "property_type", "bedrooms"])
    dropped_required = before_required_drop - len(df)
    if dropped_required:
        logger.warning("Dropped markets trends price rows missing required values | rows=%s", dropped_required)

    duplicate_columns = ["area_id", "period_end", "property_type", "bedrooms"]
    before_deduplicate = len(df)
    df = df.drop_duplicates(subset=duplicate_columns, keep="last").reset_index(drop=True)
    dropped_duplicates = before_deduplicate - len(df)
    if dropped_duplicates:
        logger.info(
            "Dropped duplicate markets trends price rows | rows=%s | subset=%s",
            dropped_duplicates,
            duplicate_columns,
        )

    df = df.sort_values(["period_end", "area_id", "property_type", "bedrooms"], ignore_index=True)

    logger.info(
        "Activity completed | activity=transform_markets_trends_price | input_records=%s | output_rows=%s",
        len(records),
        len(df),
    )
    return df


def load_transform_markets_trends_price(data_dir="data", version="all", run_date=None):
    """Load raw markets trends price data and return a cleaned DataFrame."""
    logger.info(
        "Activity started | activity=load_transform_markets_trends_price | data_dir=%s | version=%s | run_date=%s",
        data_dir,
        version,
        run_date,
    )
    records = load_endpoint_records(
        data_dir=data_dir,
        endpoint=MARKETS_TRENDS_PRICE_ENDPOINT,
        version=version,
        run_date=run_date,
    )
    df = transform_markets_trends_price(records)
    logger.info("Activity completed | activity=load_transform_markets_trends_price | rows=%s", len(df))
    return df


def load_transform_save_markets_trends_price(data_dir="data", version="all", run_date=None):
    """Load raw markets trends price records, transform them, save clean output, and return the DataFrame."""
    logger.info("Activity started | activity=load_transform_save_markets_trends_price")
    df = load_transform_markets_trends_price(data_dir=data_dir, version=version, run_date=run_date)
    save_clean_dataframe(
        df,
        data_dir=data_dir,
        endpoint=MARKETS_TRENDS_PRICE_ENDPOINT,
        run_date=run_date,
    )
    logger.info("Activity completed | activity=load_transform_save_markets_trends_price | rows=%s", len(df))
    return df

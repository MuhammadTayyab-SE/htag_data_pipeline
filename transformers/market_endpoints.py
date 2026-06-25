import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from htag_data_pipeline.endpoints import ENDPOINTS
from htag_data_pipeline.json_storage import endpoint_to_folder

from .__utils__ import find_latest_date_dir, load_endpoint_records, save_clean_dataframe


logger = logging.getLogger(__name__)


IDENTITY_COLUMNS = ["area_id", "period_end", "property_type", "dwelling_type", "bedrooms"]


@dataclass(frozen=True)
class EndpointTransformConfig:
    path: str
    table: str
    columns: list[str]
    on_conflict: list[str]

    @property
    def endpoint(self):
        return endpoint_to_folder(self.path)

    @property
    def raw_endpoint_candidates(self):
        candidates = [self.endpoint, self.table]
        singular_market = self.endpoint.replace("markets_", "market_", 1)
        candidates.append(singular_market)
        return list(dict.fromkeys(candidate for candidate in candidates if candidate))

    @property
    def numeric_columns(self):
        return [
            column
            for column in self.columns
            if column not in {"area_id", "period_end", "property_type", "dwelling_type", "bedrooms"}
        ]

    @property
    def required_columns(self):
        return [column for column in self.on_conflict if column in self.columns]

    @property
    def duplicate_columns(self):
        return [column for column in IDENTITY_COLUMNS if column in self.columns]

    @property
    def sort_columns(self):
        return [
            column
            for column in ["period_end", "area_id", "property_type", "dwelling_type", "bedrooms"]
            if column in self.columns
        ]


def get_endpoint_config(endpoint):
    endpoint_config = endpoint if isinstance(endpoint, dict) else next(
        (config for config in ENDPOINTS if config.get("path") == endpoint),
        None,
    )
    if not endpoint_config:
        raise ValueError(f"Market endpoint is not configured in endpoints.py: {endpoint}")
    return endpoint_config


def build_endpoint_transform_config(endpoint, columns):
    endpoint_config = get_endpoint_config(endpoint)
    if not columns:
        raise ValueError(f"Transformer columns are required for endpoint: {endpoint_config['path']}")

    return EndpointTransformConfig(
        path=endpoint_config["path"],
        table=endpoint_config["table"],
        columns=list(columns),
        on_conflict=list(endpoint_config.get("on_conflict") or []),
    )


def market_endpoint_date_dir(data_dir="data", run_date=None):
    return Path(data_dir) / str(run_date) if run_date else find_latest_date_dir(data_dir)


def resolve_market_endpoint_folder(config, data_dir="data", run_date=None):
    """Return the endpoint folder that contains raw data for this endpoint."""
    date_dir = market_endpoint_date_dir(data_dir=data_dir, run_date=run_date)
    for endpoint in config.raw_endpoint_candidates:
        if (date_dir / endpoint / "raw").exists():
            return endpoint

    return config.endpoint


def load_market_endpoint_records(config, data_dir="data", version="all", run_date=None):
    date_dir = market_endpoint_date_dir(data_dir=data_dir, run_date=run_date)
    last_error = None
    for endpoint in config.raw_endpoint_candidates:
        endpoint_dir = date_dir / endpoint / "raw"
        if not endpoint_dir.exists():
            last_error = FileNotFoundError(f"Endpoint directory not found: {endpoint_dir}")
            logger.info(
                "Raw endpoint folder not found; trying next candidate | endpoint=%s | candidate=%s",
                config.path,
                endpoint,
            )
            continue

        try:
            return load_endpoint_records(
                data_dir=data_dir,
                endpoint=endpoint,
                version=version,
                run_date=run_date,
            )
        except FileNotFoundError as error:
            last_error = error
            logger.info(
                "Raw endpoint files not found; trying next candidate | endpoint=%s | candidate=%s",
                config.path,
                endpoint,
            )

    raise last_error


def transform_market_endpoint_records(records, endpoint, columns):
    config = build_endpoint_transform_config(endpoint, columns)
    logger.info(
        "Activity started | activity=transform_market_endpoint_records | endpoint=%s | input_records=%s",
        config.path,
        len(records),
    )
    df = pd.DataFrame(records)

    if df.empty:
        logger.warning("No market endpoint records available to transform | endpoint=%s", config.path)
        return pd.DataFrame(columns=config.columns)

    for column in config.columns:
        if column not in df.columns:
            logger.warning(
                "Expected market endpoint column missing; filling with NA | endpoint=%s | column=%s",
                config.path,
                column,
            )
            df[column] = pd.NA

    source_columns = [column for column in df.columns if column.startswith("_source_")]
    df = df[config.columns + source_columns]

    for column in ["area_id", "property_type", "dwelling_type", "bedrooms"]:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    if "area_id" in df.columns:
        df["area_id"] = df["area_id"].str.upper()
    if "property_type" in df.columns:
        df["property_type"] = df["property_type"].str.lower()
    if "dwelling_type" in df.columns:
        df["dwelling_type"] = df["dwelling_type"].str.lower()
    if "period_end" in df.columns:
        df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce", utc=True).dt.date

    for column in config.numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    before_required_drop = len(df)
    df = df.dropna(subset=config.required_columns)
    dropped_required = before_required_drop - len(df)
    if dropped_required:
        logger.warning(
            "Dropped market endpoint rows missing required values | endpoint=%s | rows=%s | subset=%s",
            config.path,
            dropped_required,
            config.required_columns,
        )

    before_deduplicate = len(df)
    df = df.drop_duplicates(subset=config.duplicate_columns, keep="last").reset_index(drop=True)
    dropped_duplicates = before_deduplicate - len(df)
    if dropped_duplicates:
        logger.info(
            "Dropped duplicate market endpoint rows | endpoint=%s | rows=%s | subset=%s",
            config.path,
            dropped_duplicates,
            config.duplicate_columns,
        )

    if config.sort_columns:
        df = df.sort_values(config.sort_columns, ignore_index=True)

    logger.info(
        "Activity completed | activity=transform_market_endpoint_records | endpoint=%s | input_records=%s | output_rows=%s",
        config.path,
        len(records),
        len(df),
    )
    return df


def load_transform_market_endpoint(endpoint, columns, data_dir="data", version="all", run_date=None):
    config = build_endpoint_transform_config(endpoint, columns)
    logger.info(
        "Activity started | activity=load_transform_market_endpoint | endpoint=%s | data_dir=%s | version=%s | run_date=%s",
        config.path,
        data_dir,
        version,
        run_date,
    )
    records = load_market_endpoint_records(config, data_dir=data_dir, version=version, run_date=run_date)
    df = transform_market_endpoint_records(records, config.path, config.columns)
    logger.info(
        "Activity completed | activity=load_transform_market_endpoint | endpoint=%s | rows=%s",
        config.path,
        len(df),
    )
    return df


def load_transform_save_market_endpoint(endpoint, columns, data_dir="data", version="all", run_date=None):
    config = build_endpoint_transform_config(endpoint, columns)
    logger.info("Activity started | activity=load_transform_save_market_endpoint | endpoint=%s", config.path)
    df = load_transform_market_endpoint(
        config.path,
        config.columns,
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
    save_clean_dataframe(
        df,
        data_dir=data_dir,
        endpoint=resolve_market_endpoint_folder(config, data_dir=data_dir, run_date=run_date),
        run_date=run_date,
    )
    logger.info(
        "Activity completed | activity=load_transform_save_market_endpoint | endpoint=%s | rows=%s",
        config.path,
        len(df),
    )
    return df

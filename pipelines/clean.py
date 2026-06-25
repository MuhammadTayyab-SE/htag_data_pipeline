import logging
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.endpoints import ENDPOINTS
from htag_data_pipeline.pipeline_config import enabled_endpoints_for_step, load_pipeline_config
from htag_data_pipeline.transformers.localities import load_transform_save_localities
from htag_data_pipeline.transformers.market_registry import get_market_endpoint_transformer
from htag_data_pipeline.transformers.market_trends_price import load_transform_save_market_trends_price


logger = logging.getLogger(__name__)


def clean_localities_pipeline(data_dir="data", version="all", run_date=None):
    """Clean raw locality JSON files and overwrite clean locality CSV."""
    logger.info(
        "Pipeline started | pipeline=clean_localities | data_dir=%s | version=%s | run_date=%s",
        data_dir,
        version,
        run_date,
    )
    df = load_transform_save_localities(
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
    logger.info("Pipeline completed | pipeline=clean_localities | rows=%s", len(df))
    return df


def clean_market_trends_price_pipeline(data_dir="data", version="all", run_date=None):
    """Clean raw markets trends price JSON files and overwrite clean CSV."""
    logger.info(
        "Pipeline started | pipeline=clean_market_trends_price | data_dir=%s | version=%s | run_date=%s",
        data_dir,
        version,
        run_date,
    )
    df = load_transform_save_market_trends_price(
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
    logger.info("Pipeline completed | pipeline=clean_market_trends_price | rows=%s", len(df))
    return df


def clean_endpoint_pipeline(endpoint, data_dir="data", version="all", run_date=None):
    """Clean one configured HTAG market endpoint and overwrite its clean CSV."""
    endpoint_path = endpoint.get("path") if isinstance(endpoint, dict) else endpoint
    transformer = get_market_endpoint_transformer(endpoint_path)
    logger.info(
        "Pipeline started | pipeline=clean_endpoint | endpoint=%s | data_dir=%s | version=%s | run_date=%s",
        endpoint_path,
        data_dir,
        version,
        run_date,
    )
    df = transformer(
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
    logger.info("Pipeline completed | pipeline=clean_endpoint | endpoint=%s | rows=%s", endpoint_path, len(df))
    return df


def clean_all_endpoints_pipeline(
    endpoints=None,
    data_dir="data",
    version="all",
    run_date=None,
    pipeline_config=None,
):
    """Clean all configured HTAG market endpoints enabled for the clean step."""
    pipeline_config = pipeline_config or load_pipeline_config()
    configured_endpoints = enabled_endpoints_for_step(pipeline_config, "clean", endpoints or ENDPOINTS)
    dataframes = {}

    logger.info(
        "Pipeline started | pipeline=clean_all_endpoints | endpoints=%s | data_dir=%s | version=%s | run_date=%s",
        len(configured_endpoints),
        data_dir,
        version,
        run_date,
    )

    for endpoint in configured_endpoints:
        endpoint_path = endpoint["path"]
        dataframes[endpoint_path] = clean_endpoint_pipeline(
            endpoint,
            data_dir=data_dir,
            version=version,
            run_date=run_date,
        )

    logger.info("Pipeline completed | pipeline=clean_all_endpoints | endpoints=%s", len(dataframes))
    return dataframes
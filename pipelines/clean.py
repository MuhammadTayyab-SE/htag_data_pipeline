import logging
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.transformers.localities import load_transform_save_localities
from htag_data_pipeline.transformers.markets_trends_price import load_transform_save_markets_trends_price


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


def clean_markets_trends_price_pipeline(data_dir="data", version="all", run_date=None):
    """Clean raw markets trends price JSON files and overwrite clean CSV."""
    logger.info(
        "Pipeline started | pipeline=clean_markets_trends_price | data_dir=%s | version=%s | run_date=%s",
        data_dir,
        version,
        run_date,
    )
    df = load_transform_save_markets_trends_price(
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )
    logger.info("Pipeline completed | pipeline=clean_markets_trends_price | rows=%s", len(df))
    return df

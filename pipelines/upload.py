import logging
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.outbound.localities import push_localities_to_supabase
from htag_data_pipeline.outbound.endpoints import push_all_endpoints_to_supabase, push_endpoint_to_supabase


logger = logging.getLogger(__name__)


def upload_localities_pipeline(data_dir="data", run_date=None, batch_size=1000):
    """Upload clean locality CSV data into Supabase."""
    logger.info(
        "Pipeline started | pipeline=upload_localities | data_dir=%s | run_date=%s | batch_size=%s",
        data_dir,
        run_date,
        batch_size,
    )

    responses = push_localities_to_supabase(
        data_dir=data_dir,
        run_date=run_date,
        batch_size=batch_size,
    )
    uploaded_count = sum(getattr(response, "count", 0) or 0 for response in responses)
    logger.info(
        "Pipeline completed | pipeline=upload_localities | batches=%s | uploaded_count=%s",
        len(responses),
        uploaded_count,
    )
    return responses


def upload_endpoint_pipeline(endpoint, data_dir="data", run_date=None, batch_size=1000):
    """Upload one configured endpoint clean CSV into Supabase."""
    logger.info(
        "Pipeline started | pipeline=upload_endpoint | endpoint=%s | data_dir=%s | run_date=%s | batch_size=%s",
        endpoint.get("path") if isinstance(endpoint, dict) else endpoint,
        data_dir,
        run_date,
        batch_size,
    )
    responses = push_endpoint_to_supabase(
        endpoint,
        data_dir=data_dir,
        run_date=run_date,
        batch_size=batch_size,
    )
    uploaded_count = sum(getattr(response, "count", 0) or 0 for response in responses)
    logger.info(
        "Pipeline completed | pipeline=upload_endpoint | batches=%s | uploaded_count=%s",
        len(responses),
        uploaded_count,
    )
    return responses


def upload_all_endpoints_pipeline(endpoints=None, data_dir="data", run_date=None, batch_size=1000):
    """Upload all configured endpoint clean CSV files into Supabase."""
    logger.info(
        "Pipeline started | pipeline=upload_all_endpoints | data_dir=%s | run_date=%s | batch_size=%s",
        data_dir,
        run_date,
        batch_size,
    )
    responses_by_endpoint = push_all_endpoints_to_supabase(
        endpoints=endpoints,
        data_dir=data_dir,
        run_date=run_date,
        batch_size=batch_size,
    )
    uploaded_count = sum(
        getattr(response, "count", 0) or 0
        for responses in responses_by_endpoint.values()
        for response in responses
    )
    logger.info(
        "Pipeline completed | pipeline=upload_all_endpoints | endpoints=%s | uploaded_count=%s",
        len(responses_by_endpoint),
        uploaded_count,
    )
    return responses_by_endpoint

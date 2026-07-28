import logging
import datetime
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from htag_data_pipeline.pipelines.clean import clean_all_endpoints_pipeline, clean_localities_pipeline
from htag_data_pipeline.pipelines.ingest import ingest_all_pipeline, ingest_localities_pipeline
from htag_data_pipeline.pipelines.upload import upload_all_endpoints_pipeline, upload_localities_pipeline
from htag_data_pipeline.logging_utils import setup_pipeline_logging
from htag_data_pipeline.pipeline_config import (
    enabled_endpoints_for_step,
    load_pipeline_config,
    pipeline_step_enabled,
)


today_date = datetime.date.today().strftime("%Y%m%d")
logger = logging.getLogger(__name__)


def console_action(message):
    print(message, flush=True)


def run_all_pipelines(data_dir="data", run_date=None, upload=True, config_path=None, locality_limit=500):
    run_date = run_date or today_date
    
    # setting up the logging
    log_path = setup_pipeline_logging()

    # loading pipeline configuration
    pipeline_config = load_pipeline_config(config_path)

    logger.info(
        "Pipeline run started | data_dir=%s | run_date=%s | upload_enabled=%s | config_path=%s | log_file=%s",
        data_dir,
        run_date,
        upload,
        config_path,
        log_path,
    )
    console_action(f"Pipeline started | run_date={run_date} | data_dir={data_dir}")

    try:
        # Locality Ingestion code
        if pipeline_step_enabled(pipeline_config, "locality", "ingest", default=True):
            logger.info("Stage started | stage=ingest_localities")
            console_action("Stage started | ingest_localities")
            locality_ingestion = ingest_localities_pipeline(data_dir=data_dir, run_date=run_date)

            if locality_ingestion:
                logger.info("Stage completed | stage=ingest_localities")
                console_action("Stage completed | ingest_localities")
            else:
                logger.error("Stage failed | stage=ingest_localities")
                console_action("Stage failed | ingest_localities | check log file")
                return False
        else:
            logger.info("Stage skipped | stage=ingest_localities | reason=config_disabled")
            console_action("Stage skipped | ingest_localities | config disabled")
        
        # Locality Clean Code
        if pipeline_step_enabled(pipeline_config, "locality", "clean", default=True):

            logger.info("Stage started | stage=clean_localities")
            console_action("Stage started | clean_localities")

            dataframe = clean_localities_pipeline(data_dir=data_dir, version="all", run_date=run_date)
            if len(dataframe):
                logger.info("Stage completed | stage=clean_localities | cleaned_rows=%s", len(dataframe))
                console_action(f"Stage completed | clean_localities | rows={len(dataframe)}")
            else:
                logger.warning("Stage completed with no rows | stage=clean_localities")
                console_action("Stage failed | clean_localities | no rows | check log file")
                return False
        else:
            logger.info("Stage skipped | stage=clean_localities | reason=config_disabled")
            console_action("Stage skipped | clean_localities | config disabled")

        # Other Endpoints Ingestion code
        ingest_endpoints = enabled_endpoints_for_step(pipeline_config, "ingest")
        if ingest_endpoints:
            logger.info("Stage started | stage=ingest_endpoints | endpoints=%s", len(ingest_endpoints))
            console_action(f"Stage started | ingest_endpoints | endpoints={len(ingest_endpoints)}")
            ingest_all_pipeline(
                data_dir=data_dir,
                run_date=run_date,
                endpoints=ingest_endpoints,
                pipeline_config=pipeline_config,
                locality_limit=locality_limit,
            )
            logger.info("Stage completed | stage=ingest_endpoints | endpoints=%s", len(ingest_endpoints))
            console_action(f"Stage completed | ingest_endpoints | endpoints={len(ingest_endpoints)}")
        else:
            logger.info("Stage skipped | stage=ingest_endpoints | reason=no_config_enabled_endpoints")
            console_action("Stage skipped | ingest_endpoints | no enabled endpoints")

        # Other Endpoints clean code
        clean_endpoints = enabled_endpoints_for_step(pipeline_config, "clean")
        if clean_endpoints:
            logger.info("Stage started | stage=clean_endpoints | endpoints=%s", len(clean_endpoints))
            console_action(f"Stage started | clean_endpoints | endpoints={len(clean_endpoints)}")

            dataframes_by_endpoint = clean_all_endpoints_pipeline(
                endpoints=clean_endpoints,
                data_dir=data_dir,
                version="all",
                run_date=run_date,
                pipeline_config=pipeline_config,
            )
            cleaned_rows = sum(len(dataframe) for dataframe in dataframes_by_endpoint.values())

            logger.info(
                "Stage completed | stage=clean_endpoints | endpoints=%s | cleaned_rows=%s",
                len(dataframes_by_endpoint),
                cleaned_rows,
            )
            console_action(f"Stage completed | clean_endpoints | rows={cleaned_rows}")
        else:
            logger.info("Stage skipped | stage=clean_endpoints | reason=no_config_enabled_endpoints")
            console_action("Stage skipped | clean_endpoints | no enabled endpoints")


        # Locality Upload Code
        if upload and pipeline_step_enabled(pipeline_config, "locality", "upload", default=True):
            logger.info("Stage started | stage=upload_localities")
            console_action("Stage started | upload_localities")
            localities_upload = upload_localities_pipeline(data_dir=data_dir, run_date=run_date, batch_size=1000)
            uploaded_count = sum(getattr(response, "count", 0) or 0 for response in localities_upload)
            logger.info(
                "Stage completed | stage=upload_localities | batches=%s | uploaded_count=%s",
                len(localities_upload),
                uploaded_count,
            )
            if uploaded_count > 0:
                console_action(f"Stage completed | upload_localities | uploaded={uploaded_count}")
            else:
                logger.warning("Upload completed but Supabase reported zero affected rows")
                console_action("Stage completed | upload_localities | uploaded=0")
        else:
            logger.info("Stage skipped | stage=upload_localities | reason=upload_or_config_disabled")
            console_action("Stage skipped | upload_localities | upload or config disabled")
        
        # Upload Endpoints Code
        upload_endpoints = enabled_endpoints_for_step(pipeline_config, "upload")
        if upload and upload_endpoints:

            logger.info("Stage started | stage=upload_endpoints | endpoints=%s", len(upload_endpoints))
            console_action(f"Stage started | upload_endpoints | endpoints={len(upload_endpoints)}")

            responses_by_endpoint = upload_all_endpoints_pipeline(
                endpoints=upload_endpoints,
                data_dir=data_dir,
                run_date=run_date,
                batch_size=1000,
            )
            uploaded_count = sum(
                getattr(response, "count", 0) or 0
                for responses in responses_by_endpoint.values()
                for response in responses
            )

            logger.info(
                "Stage completed | stage=upload_endpoints | endpoints=%s | uploaded_count=%s",
                len(responses_by_endpoint),
                uploaded_count,
            )
            console_action(f"Stage completed | upload_endpoints | uploaded={uploaded_count}")
            
        else:
            logger.info("Stage skipped | stage=upload_endpoints | reason=upload_or_config_disabled")
            console_action("Stage skipped | upload_endpoints | upload or config disabled")

        logger.info("Pipeline run completed successfully")
        console_action("Pipeline finished successfully")
        return True
    
    except Exception:
        logger.exception("Pipeline run failed unexpectedly")
        console_action("Pipeline failed | check log file")
        return False

if __name__ == "__main__":
    run_all_pipelines(data_dir="data", run_date=today_date)


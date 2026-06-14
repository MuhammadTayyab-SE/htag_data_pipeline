import logging
import datetime
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from htag_data_pipeline.pipelines.clean import clean_localities_pipeline
from htag_data_pipeline.pipelines.ingest import ingest_all_pipeline, ingest_localities_pipeline
from htag_data_pipeline.pipelines.upload import upload_localities_pipeline
from htag_data_pipeline.logging_utils import setup_pipeline_logging


today_date = datetime.date.today().strftime("%Y%m%d")
logger = logging.getLogger(__name__)

# def run_all_pipelines(data_dir="data", run_date=None, upload=True):
#     """Run ingest, clean, and upload pipeline stages in order."""
    
#     print("Ingesting raw API data...")
#     raw_outputs = ingest_all_pipeline(data_dir=data_dir, run_date=run_date)
#     print(f"Saved {len(raw_outputs)} raw endpoint output(s)")

#     print("Cleaning locality data...")
#     clean_localities = clean_localities_pipeline(data_dir=data_dir, run_date=run_date)
#     print(f"Prepared {len(clean_localities)} clean locality row(s)")

#     upload_responses = []
#     if upload:
#         print("Uploading localities to Supabase...")
#         upload_responses = upload_localities_pipeline(data_dir=data_dir, run_date=run_date)
#         print(f"Uploaded localities in {len(upload_responses)} batch(es)")

#     return {
#         "raw_outputs": raw_outputs,
#         "clean_localities": clean_localities,
#         "upload_responses": upload_responses,
#     }


def run_all_pipelines(data_dir="data", run_date=None, upload=True):
    run_date = run_date or today_date
    log_path = setup_pipeline_logging()

    logger.info(
        "Pipeline run started | data_dir=%s | run_date=%s | upload_enabled=%s | log_file=%s",
        data_dir,
        run_date,
        upload,
        log_path,
    )

    try:
        logger.info("Stage started | stage=ingest_localities")
        locality_ingestion = ingest_localities_pipeline(data_dir=data_dir, run_date=run_date)
        if locality_ingestion:
            logger.info("Stage completed | stage=ingest_localities")
            print("Data successfully ingested for reference/locality endpoint")
        else:
            logger.error("Stage failed | stage=ingest_localities")
            print("Exception raised during data ingestion from reference/locality endpoint. Please check log file.")
            return False

        logger.info("Stage started | stage=clean_localities")
        dataframe = clean_localities_pipeline(data_dir=data_dir, version="all", run_date=run_date)
        if len(dataframe):
            logger.info("Stage completed | stage=clean_localities | cleaned_rows=%s", len(dataframe))
            print("Data successfully cleaned for reference/locality endpoint")
        else:
            logger.warning("Stage completed with no rows | stage=clean_localities")
            print("Exception raised during data processing from reference/locality endpoint. Please check log file.")
            return False

        if upload:
            logger.info("Stage started | stage=upload_localities")
            localities_upload = upload_localities_pipeline(data_dir=data_dir, run_date=run_date, batch_size=1000)
            uploaded_count = sum(getattr(response, "count", 0) or 0 for response in localities_upload)
            logger.info(
                "Stage completed | stage=upload_localities | batches=%s | uploaded_count=%s",
                len(localities_upload),
                uploaded_count,
            )
            if uploaded_count > 0:
                print("Data successfully saved into Supabase")
            else:
                logger.warning("Upload completed but Supabase reported zero affected rows")
        else:
            logger.info("Stage skipped | stage=upload_localities | reason=upload_disabled")

        logger.info("Pipeline run completed successfully")
        return True
    except Exception:
        logger.exception("Pipeline run failed unexpectedly")
        print("Pipeline failed. Please check log file.")
        return False

if __name__ == "__main__":
    run_all_pipelines()

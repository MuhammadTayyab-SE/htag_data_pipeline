import logging
import datetime
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from htag_data_pipeline.pipelines.clean import clean_localities_pipeline
from htag_data_pipeline.pipelines.ingest import ingest_all_pipeline, ingest_localities_pipeline
from htag_data_pipeline.pipelines.upload import upload_localities_pipeline


today_date = datetime.date.today().strftime("%Y%m%d")
start_time = datetime.datetime.now().strftime("%I_%M_%S%p")
log_filename = f"./logging/htag_data_pipeline_{today_date}_{start_time}_pipeline.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
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

    locality_ingestion = ingest_localities_pipeline(data_dir=data_dir, run_date=run_date)
    if len(locality_ingestion):
        print("Data successfully ingested for reference/locality endpoint")

        dataframe = clean_localities_pipeline(data_dir=data_dir, version="all", run_date=run_date)

        if len(dataframe):
            print("Data successfully cleaned for reference/locality endpoint")

            if upload:
                localities_upload = upload_localities_pipeline(data_dir=data_dir, run_date=run_date, batch_size=1000)
                if localities_upload[-1].count > 0:
                    print("Data Successfully save into Supabase")

        else:
            print("Exception raised during data processing from reference/locality endpoint. Plesae check log file.")
    else:
        print("Exception raised during data ingestion from reference/locality endpoint. Plesae check log file.")

if __name__ == "__main__":
    run_all_pipelines()

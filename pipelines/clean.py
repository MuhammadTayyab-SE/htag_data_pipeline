import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from htag_data_pipeline.transformers.localities import load_transform_save_localities


def clean_localities_pipeline(data_dir="data", version="all", run_date=None):
    """Clean raw locality JSON files and overwrite clean locality CSV."""
    return load_transform_save_localities(
        data_dir=data_dir,
        version=version,
        run_date=run_date,
    )

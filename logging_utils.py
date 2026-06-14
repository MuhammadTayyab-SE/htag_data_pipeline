import logging
from datetime import datetime
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_pipeline_logging(log_dir=None, level=logging.INFO):
    """Configure file logging for one pipeline run and return the log path."""
    package_dir = Path(__file__).resolve().parent
    log_dir = Path(log_dir) if log_dir else package_dir / "logging"
    log_dir.mkdir(parents=True, exist_ok=True)

    run_stamp = datetime.now().strftime("%Y%m%d_%I_%M_%S%p")
    log_path = log_dir / f"htag_data_pipeline_{run_stamp}_pipeline.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in list(root_logger.handlers):
        if getattr(handler, "_htag_pipeline_handler", False):
            root_logger.removeHandler(handler)
            handler.close()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler._htag_pipeline_handler = True
    root_logger.addHandler(file_handler)

    return log_path

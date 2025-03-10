import functools
import logging
import os
from datetime import datetime

from azure.storage.blob import BlobServiceClient
from opencensus.ext.azure.log_exporter import AzureLogHandler

AZURE_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-5s | %(filename)s:%(lineno)s | %(message)s"
)
LOG_FILE_PATH = "/tmp/logs.txt"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelname == "WARNING":
            record.levelname = "WARN"
        return super().format(record)


def setup_logger(name: str) -> logging.Logger:
    """Configure and return logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode="w")
    file_handler.setFormatter(CustomFormatter(AZURE_LOG_FORMAT))
    logger.addHandler(file_handler)

    app_insights_conn_str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not app_insights_conn_str:
        logger.error("Missing Application Insights connection string!")
        raise RuntimeError()

    azure_handler = AzureLogHandler(connection_string=app_insights_conn_str)
    azure_handler.setFormatter(logging.Formatter(AZURE_LOG_FORMAT))
    logger.addHandler(azure_handler)

    return logger


def upload_logs_to_blob():
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        logger.error("Azure storage connection string missing. Logs won't be uploaded.")
        raise RuntimeError()

    blob_name = f"logs-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

    try:
        blobl_service_client = BlobServiceClient.from_connection_string(conn_str)
        blob_client = blobl_service_client.get_blob_client(
            container="function-logs", blob=blob_name
        )

        with open(LOG_FILE_PATH, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        logger.info(f"Uploaded logs to Azure Blob storage as {blob_name}")

    except Exception as e:
        logger.error(f"Failed to upload logs to Azure Blob Storage: {e}", exc_info=True)


logger = setup_logger(__name__)


def log(func):
    """Decorator to log function calls and exceptions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.debug(
            f"Calling function '{func.__name__}' with args: {args}, kwargs: {kwargs}"
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function '{func.__name__}' returned: {result}")
            return result
        except Exception as e:
            logger.exception(
                f"Exception in '{func.__name__}' with args {args}, kwargs {kwargs}: {e}"
            )
            raise

    return wrapper

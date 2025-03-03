import functools
import logging
import os

from opencensus.ext.azure.log_exporter import AzureLogHandler

AZURE_LOG_FORMAT = "%(levelname)s | %(filename)s:%(lineno)s | %(message)s"


def setup_logger(name: str) -> logging.Logger:
    """Configure and return logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        azure_handler = AzureLogHandler(
            connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        )
        azure_handler.setLevel(logging.DEBUG)
        azure_handler.setFormatter(logging.Formatter(AZURE_LOG_FORMAT))
        logger.addHandler(azure_handler)
    else:
        logger.error("No Application Insights connection string")

    return logger


logger = setup_logger(__name__)


def log(func):
    """Decorator to log function calls and exceptions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.debug("Function '%s' called with args: %s", func.__name__, signature)
        try:
            result = func(*args, **kwargs)
            logger.debug("Function '%s' returned: %s", func.__name__, result)
            return result
        except Exception as e:
            logger.error(
                "Exception in '%s' (args: %s): %s",
                func.__name__,
                signature,
                str(e),
                exc_info=True,
            )
            raise

    return wrapper

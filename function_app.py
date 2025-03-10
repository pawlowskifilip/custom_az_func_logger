import azure.functions as func

from src.custom_logger_tmp import log, logger, upload_logs_to_blob

app = func.FunctionApp()


@log
def testing(a: int, b: int) -> int:
    logger.info("Inside testing function")
    suming = a + b
    return suming


# version 0.0.2
@app.route(route="AzLogger", auth_level=func.AuthLevel.ANONYMOUS)
def AzLogger(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Python HTTP trigger function processed a request.")
    logger.warning("dupa")

    try:
        testing(10, 20)
        testing(10, "s")
    finally:
        upload_logs_to_blob()

    return func.HttpResponse(
        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        status_code=200,
    )

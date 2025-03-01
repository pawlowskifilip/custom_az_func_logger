import datetime
import json
import logging

import azure.functions as func

app = func.FunctionApp()


# version 0.0.1
@app.route(route="AzLogger", auth_level=func.AuthLevel.ANONYMOUS)
def AzLogger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    number_list = [x for x in range(10)]
    logging.info(number_list)

    return func.HttpResponse(
        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        status_code=200,
    )

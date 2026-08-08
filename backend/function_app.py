import azure.functions as func

app = func.FunctionApp()

import functions.email_ingestion
import functions.pods_extractor
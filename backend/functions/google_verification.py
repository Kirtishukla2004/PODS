import azure.functions as func
from function_app import app

VERIFICATION_CONTENT = "google-site-verification: google4230e103043b7328.html"


@app.route(route="google4230e103043b7328.html", auth_level=func.AuthLevel.ANONYMOUS)
def GoogleVerification(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(VERIFICATION_CONTENT, mimetype="text/html")

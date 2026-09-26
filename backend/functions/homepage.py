import azure.functions as func
from function_app import app

HOMEPAGE_HTML = """<!DOCTYPE html>
<html>
<head><title>PODS</title></head>
<body>
<h1>PODS</h1>
<p>Internal document processing service.</p>
</body>
</html>"""


@app.route(route="/", auth_level=func.AuthLevel.ANONYMOUS)
def Homepage(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(HOMEPAGE_HTML, mimetype="text/html")

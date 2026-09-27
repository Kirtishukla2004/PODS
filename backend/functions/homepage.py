import azure.functions as func
from function_app import app

HOMEPAGE_HTML = """<!DOCTYPE html>
<html>
<head><title>PODS</title></head>
<body>
<h1>PODS (Processing & Organization Document Service)</h1>
<p>PODS is an internal tool used by PODS to automatically process,
classify, and organize uploaded documents using Google Drive integration.
It reads and organizes files a user has granted access to, and does not
share data with third parties.</p>
<p><a href="https://yourdomain.com/privacy">Privacy Policy</a></p>
</body>
</html>"""


@app.route(route="/", auth_level=func.AuthLevel.ANONYMOUS)
def Homepage(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(HOMEPAGE_HTML, mimetype="text/html")

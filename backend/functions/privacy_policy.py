import azure.functions as func
from function_app import app

PRIVACY_HTML = """<!DOCTYPE html>
<html>
<head><title>Privacy Policy - PODS</title></head>
<body style="font-family: sans-serif; max-width: 700px; margin: 40px auto; line-height: 1.6;">
<h1>Privacy Policy</h1>
<p><em>Last updated: September 2026</em></p>

<p>This application ("PODS") accesses Gmail data solely for internal
document processing. It reads unread emails and their attachments from
a connected Gmail account, uploads relevant files to secure Azure Blob
Storage, and queues them for further processing.</p>

<h2>What data we access</h2>
<ul>
  <li>Email subject, sender, date, and body text</li>
  <li>Email attachments (PDFs, documents, etc.)</li>
</ul>

<h2>How we use it</h2>
<p>Data is used exclusively to extract and process documents attached
to or contained within emails, as part of an internal automated
workflow. Emails are marked as read once processed.</p>

<h2>What we don't do</h2>
<p>We do not sell, share, or use this data for advertising. Data is not
shared with third parties beyond internal storage and processing
infrastructure.</p>

<h2>Contact</h2>
<p>For questions about this policy, contact: your-email@example.com</p>
</body>
</html>"""


@app.route(route="privacy-policy", auth_level=func.AuthLevel.ANONYMOUS)
def PrivacyPolicy(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(PRIVACY_HTML, mimetype="text/html")

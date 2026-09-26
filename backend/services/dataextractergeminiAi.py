import os
import logging

from google import genai
from google.genai import types, errors
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_exponential,
    stop_after_attempt,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Primary + fallback model, both overridable via app settings without a redeploy.
# When Google deprecates/renames a model again, just update these env vars.
PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-3.6-flash")
FALLBACK_MODEL = os.environ.get(
    "GEMINI_FALLBACK_MODEL", "models/gemini-2.5-flash-lite")

MIME_TYPES = {
    "pdf": "application/pdf",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "tiff": "image/tiff",
    "bmp": "image/bmp",
}

PROMPT = (
    "convert the document data into english language first then extract "
    "data convert to json format return in json format"
)


@retry(
    # only retry on 5xx (e.g. 503 overload)
    retry=retry_if_exception_type(errors.ServerError),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(4),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _call_gemini(model: str, contents, config):
    return client.models.generate_content(model=model, contents=contents, config=config)


def extract_document(file_bytes: bytes, blob_name: str) -> str:
    extension = blob_name.lower().split(".")[-1]

    if extension not in MIME_TYPES:
        raise ValueError(f"Unsupported file type: {extension}")

    contents = [
        PROMPT,
        types.Part.from_bytes(
            data=file_bytes, mime_type=MIME_TYPES[extension]),
    ]
    config = types.GenerateContentConfig(response_mime_type="application/json")

    try:
        response = _call_gemini(PRIMARY_MODEL, contents, config)
    except errors.ServerError:
        # Primary model kept returning 503s after retries — try the fallback model once.
        logger.warning(
            f"{PRIMARY_MODEL} unavailable after retries, falling back to {FALLBACK_MODEL}"
        )
        response = _call_gemini(FALLBACK_MODEL, contents, config)
    except errors.ClientError as e:
        if e.status_code == 404:
            logger.error(
                f"Model {PRIMARY_MODEL} not found — it may have been deprecated. "
                "Check https://ai.google.dev/gemini-api/docs/models for the current model name "
                "and update the GEMINI_MODEL app setting."
            )
        raise

    result = response.text
    logger.info(f"Extracted data for {blob_name}: {result}")
    return result

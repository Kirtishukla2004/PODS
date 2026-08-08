import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def extract_document(file_bytes: bytes, blob_name: str):
    extension = blob_name.lower().split(".")[-1]
    mime_types = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "tiff": "image/tiff",
        "bmp": "image/bmp"
    }

    if extension not in mime_types:
        raise ValueError(f"Unsupported file type: {extension}")
    prompt = """convert the document data into english language first then extract data convert to json format return in json format """
    response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        prompt,
        types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_types[extension]
        )
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
    )
    result = response.text
    print(f"Extracted data: {result}")
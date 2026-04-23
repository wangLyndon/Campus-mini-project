import json
import urllib.request
import os

PROCESSING_FUNCTION_URL = os.environ.get("PROCESSING_FUNCTION_URL")


def normalize_event(event):
    if isinstance(event, dict) and "body" in event and event["body"]:
        try:
            return json.loads(event["body"])
        except Exception:
            return event
    return event


def lambda_handler(event, context):
    event = normalize_event(event)

    if not PROCESSING_FUNCTION_URL:
        return {
            "statusCode": 500,
            "body": json.dumps("PROCESSING_FUNCTION_URL not set")
        }

    req = urllib.request.Request(
        PROCESSING_FUNCTION_URL,
        data=json.dumps(event).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode("utf-8")
    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Submission event forwarded successfully",
            "processing_response": result
        })
    }

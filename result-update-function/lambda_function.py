import json
import urllib.request
import os

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL")


def normalize_event(event):
    if isinstance(event, dict) and "body" in event and event["body"]:
        try:
            return json.loads(event["body"])
        except Exception:
            return event
    return event


def lambda_handler(event, context):
    event = normalize_event(event)

    if not DATA_SERVICE_URL:
        return {
            "statusCode": 500,
            "body": json.dumps("DATA_SERVICE_URL not set")
        }

    record_id = event.get("record_id")

    update_payload = {
        "status": event.get("status"),
        "category": event.get("category"),
        "priority": event.get("priority"),
        "note": event.get("note")
    }

    url = f"{DATA_SERVICE_URL}/records/{record_id}"

    req = urllib.request.Request(
        url,
        data=json.dumps(update_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT"
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
            "message": "Record updated successfully",
            "data_service_response": result
        })
    }

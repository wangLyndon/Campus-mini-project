import json
import urllib.request
import os
import re

RESULT_UPDATE_FUNCTION_URL = os.environ.get("RESULT_UPDATE_FUNCTION_URL")


def normalize_event(event):
    if isinstance(event, dict) and "body" in event and event["body"]:
        try:
            return json.loads(event["body"])
        except Exception:
            return event
    return event


def classify_category(title, description):
    text = f"{title} {description}".lower()

    if any(word in text for word in ["career", "internship", "recruitment"]):
        return "OPPORTUNITY"
    elif any(word in text for word in ["workshop", "seminar", "lecture"]):
        return "ACADEMIC"
    elif any(word in text for word in ["club", "society", "social"]):
        return "SOCIAL"
    else:
        return "GENERAL"


def get_priority(category):
    if category == "OPPORTUNITY":
        return "HIGH"
    elif category == "ACADEMIC":
        return "MEDIUM"
    else:
        return "NORMAL"


def valid_date_format(date_str):
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str or ""))


def lambda_handler(event, context):
    event = normalize_event(event)

    title = event.get("title")
    description = event.get("description")
    location = event.get("location")
    date = event.get("date")
    organiser_name = event.get("organiser_name")
    record_id = event.get("record_id")

    required_fields = [title, description, location, date, organiser_name]

    if any(field is None or str(field).strip() == "" for field in required_fields):
        status = "INCOMPLETE"
        category = "GENERAL"
        priority = "NORMAL"
        note = "Some required fields are missing."
    else:
        category = classify_category(title, description)
        priority = get_priority(category)

        if not valid_date_format(date):
            status = "NEEDS REVISION"
            note = "The date format must be YYYY-MM-DD."
        elif len(description.strip()) < 40:
            status = "NEEDS REVISION"
            note = "The description must be at least 40 characters long."
        else:
            status = "APPROVED"
            note = "The submission passed all checks."

    result = {
        "record_id": record_id,
        "status": status,
        "category": category,
        "priority": priority,
        "note": note
    }

    if RESULT_UPDATE_FUNCTION_URL:
        req = urllib.request.Request(
            RESULT_UPDATE_FUNCTION_URL,
            data=json.dumps(result).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            update_response = response.read().decode("utf-8")
    else:
        update_response = "RESULT_UPDATE_FUNCTION_URL not set"

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Processing completed",
            "result": result,
            "update_response": update_response
        })
    }

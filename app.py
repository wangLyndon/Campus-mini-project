from flask import Flask, request, jsonify
import requests
import urllib.request
import json

app = Flask(__name__)

DATA_SERVICE_URL = "http://172.17.0.1:5002"
SUBMISSION_EVENT_FUNCTION_URL = "https://hpauiehpmiblwyjdvxcxqruotm0ktvfi.lambda-url.ap-southeast-2.on.aws/"


@app.route("/")
def home():
    return "Workflow Service is running"


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    try:
        response = requests.post(f"{DATA_SERVICE_URL}/records", json=data)
        record_response = response.json()
        record_id = record_response["id"]

        event_payload = {
            "record_id": record_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "location": data.get("location"),
            "date": data.get("date"),
            "organiser_name": data.get("organiser_name")
        }

        req = urllib.request.Request(
            SUBMISSION_EVENT_FUNCTION_URL,
            data=json.dumps(event_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req)

        return jsonify(record_response), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/status/<record_id>", methods=["GET"])
def status(record_id):
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/records/{record_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

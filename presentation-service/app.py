from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

WORKFLOW_SERVICE_URL = "http://172.17.0.1:5001"


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    data = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "location": request.form.get("location"),
        "date": request.form.get("date"),
        "organiser_name": request.form.get("organiser_name")
    }

    try:
        response = requests.post(f"{WORKFLOW_SERVICE_URL}/submit", json=data)
        result = response.json()
        record_id = result.get("id")

        if not record_id:
            return f"Error: failed to create record. Response: {result}", 500

        return redirect(url_for("result", record_id=record_id))
    except Exception as e:
        return f"Error submitting form: {str(e)}", 500


@app.route("/result/<record_id>", methods=["GET"])
def result(record_id):
    try:
        response = requests.get(f"{WORKFLOW_SERVICE_URL}/status/{record_id}")
        result_data = response.json()

        return render_template("result.html", record=result_data)
    except Exception as e:
        return f"Error fetching result: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

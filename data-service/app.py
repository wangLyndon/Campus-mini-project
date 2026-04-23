from flask import Flask, request, jsonify
import sqlite3
import uuid
import os

app = Flask(__name__)
DB_PATH = "submissions.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            location TEXT,
            date TEXT,
            organiser_name TEXT,
            status TEXT,
            category TEXT,
            priority TEXT,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return "Data Service is running"


@app.route("/records", methods=["POST"])
def create_record():
    data = request.get_json()
    record_id = str(uuid.uuid4())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions
        (id, title, description, location, date, organiser_name, status, category, priority, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id,
        data.get("title"),
        data.get("description"),
        data.get("location"),
        data.get("date"),
        data.get("organiser_name"),
        "PENDING",
        None,
        None,
        "Submitted and waiting for processing."
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "id": record_id,
        "status": "PENDING"
    }), 201


@app.route("/records/<record_id>", methods=["GET"])
def get_record(record_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, location, date, organiser_name, status, category, priority, note
        FROM submissions
        WHERE id = ?
    """, (record_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Record not found"}), 404

    return jsonify({
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "location": row[3],
        "date": row[4],
        "organiser_name": row[5],
        "status": row[6],
        "category": row[7],
        "priority": row[8],
        "note": row[9]
    })


@app.route("/records/<record_id>", methods=["PUT"])
def update_record(record_id):
    data = request.get_json()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE submissions
        SET status = ?, category = ?, priority = ?, note = ?
        WHERE id = ?
    """, (
        data.get("status"),
        data.get("category"),
        data.get("priority"),
        data.get("note"),
        record_id
    ))
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return jsonify({"error": "Record not found"}), 404

    return jsonify({"message": "Record updated successfully"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5002)

from flask import Flask, jsonify, render_template, request
import sqlite3
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "crop_records.db"

app = Flask(__name__)

FIELDS = [
    "id", "farmer_name", "crop_name", "field_name", "area",
    "sowing_date", "harvest_date", "season", "expected_yield",
    "notes", "actual_yield", "seed_cost", "fertilizer_cost",
    "pesticide_cost", "labor_cost", "irrigation_cost",
    "other_cost", "sale_income"
]

MONEY_FIELDS = [
    "seed_cost", "fertilizer_cost", "pesticide_cost",
    "labor_cost", "irrigation_cost", "other_cost", "sale_income"
]

NUMERIC_FIELDS = ["area", "expected_yield", "actual_yield"] + MONEY_FIELDS


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id TEXT PRIMARY KEY,
                farmer_name TEXT NOT NULL,
                crop_name TEXT NOT NULL,
                field_name TEXT NOT NULL,
                area REAL NOT NULL,
                sowing_date TEXT NOT NULL,
                harvest_date TEXT DEFAULT '',
                season TEXT NOT NULL,
                expected_yield REAL DEFAULT 0,
                notes TEXT DEFAULT '',
                actual_yield REAL DEFAULT 0,
                seed_cost REAL DEFAULT 0,
                fertilizer_cost REAL DEFAULT 0,
                pesticide_cost REAL DEFAULT 0,
                labor_cost REAL DEFAULT 0,
                irrigation_cost REAL DEFAULT 0,
                other_cost REAL DEFAULT 0,
                sale_income REAL DEFAULT 0
            )
        """)


def clean_record(data):
    record = {field: str(data.get(field, "") or "").strip() for field in FIELDS}
    record["id"] = record["id"] or str(uuid4())

    for field in NUMERIC_FIELDS:
        value = record[field]
        if value == "":
            record[field] = 0.0
        else:
            record[field] = float(value)
            if record[field] < 0:
                raise ValueError(f"{field} cannot be negative")

    if not record["farmer_name"] or not record["crop_name"] or not record["field_name"]:
        raise ValueError("Farmer name, crop name and field name are required.")
    if record["area"] <= 0:
        raise ValueError("Area must be greater than 0.")
    if not record["sowing_date"] or not record["season"]:
        raise ValueError("Sowing date and season are required.")

    return record


def row_to_dict(row):
    return dict(row)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/crops")
def list_crops():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM crops ORDER BY sowing_date DESC, rowid DESC"
        ).fetchall()
    return jsonify([row_to_dict(row) for row in rows])


@app.post("/api/crops")
def create_crop():
    try:
        record = clean_record(request.get_json(silent=True) or {})
        with get_db() as conn:
            conn.execute(
                f"INSERT INTO crops ({','.join(FIELDS)}) VALUES ({','.join(['?'] * len(FIELDS))})",
                [record[field] for field in FIELDS],
            )
        return jsonify(record), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "A record with this ID already exists."}), 409


@app.put("/api/crops/<crop_id>")
def update_crop(crop_id):
    try:
        data = request.get_json(silent=True) or {}
        data["id"] = crop_id
        record = clean_record(data)

        update_fields = [field for field in FIELDS if field != "id"]
        with get_db() as conn:
            cur = conn.execute(
                f"UPDATE crops SET {','.join(f'{f}=?' for f in update_fields)} WHERE id=?",
                [record[field] for field in update_fields] + [crop_id],
            )
            if cur.rowcount == 0:
                return jsonify({"error": "Crop record not found."}), 404

        return jsonify(record)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.delete("/api/crops/<crop_id>")
def delete_crop(crop_id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM crops WHERE id=?", (crop_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Crop record not found."}), 404
    return jsonify({"message": "Record deleted."})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

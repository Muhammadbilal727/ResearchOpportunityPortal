from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Fields allowed in the database
FIELDS = [
    "title",
    "description",
    "research_area",
    "faculty_name",
    "department",
    "required_skills",
    "available_positions",
    "application_deadline",
    "status",
]

REQUIRED_FIELDS = [
    "title",
    "description",
    "research_area",
    "faculty_name",
    "department",
    "required_skills",
    "available_positions",
    "application_deadline",
]


# Connect Python to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "research_portal"),
    )


# Validate submitted information
def validate_data(data, creating=False):
    if not isinstance(data, dict) or not data:
        return "Send a non-empty JSON object."

    unknown = set(data.keys()) - set(FIELDS)
    if unknown:
        return "Unknown field(s): " + ", ".join(sorted(unknown))

    if creating:
        missing = [
            field for field in REQUIRED_FIELDS
            if field not in data
        ]
        if missing:
            return "Missing required fields: " + ", ".join(missing)

    for field in REQUIRED_FIELDS:
        if field in data:
            value = data[field]

            if isinstance(value, str) and not value.strip():
                return field + " cannot be empty."

            if value is None:
                return field + " is required."

    if "available_positions" in data:
        positions = data["available_positions"]

        if (
            isinstance(positions, bool)
            or not isinstance(positions, int)
            or positions < 1
        ):
            return "available_positions must be a positive integer."

    if "application_deadline" in data:
        try:
            deadline = data["application_deadline"]
            if not isinstance(deadline, str):
                raise ValueError()
            date.fromisoformat(deadline)
        except (ValueError, TypeError):
            return "application_deadline must use YYYY-MM-DD format."

    if "status" in data:
        if data["status"] not in ("Open", "Closed"):
            return "Status must be Open or Closed."

    return None


# Convert a database row into JSON-friendly data
def format_opportunity(row):
    result = dict(row)

    if result.get("application_deadline"):
        result["application_deadline"] = (
            result["application_deadline"].isoformat()
        )

    return result


# 1. Create an opportunity
@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    data = request.get_json(silent=True)
    error = validate_data(data, creating=True)

    if error:
        return jsonify({"error": error}), 400

    data = dict(data)
    data.setdefault("status", "Open")

    columns = list(data.keys())
    column_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        sql = (
            f"INSERT INTO opportunities ({column_names}) "
            f"VALUES ({placeholders})"
        )

        cursor.execute(sql, tuple(data[column] for column in columns))
        connection.commit()

        new_id = cursor.lastrowid

        return jsonify({
            "message": "Opportunity created successfully.",
            "id": new_id,
        }), 201

    except Error:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Error creating opportunity")
        return jsonify({"error": "Database operation failed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# 2. Retrieve all opportunities
@app.route("/api/opportunities", methods=["GET"])
def get_opportunities():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM opportunities ORDER BY id DESC"
        )
        rows = cursor.fetchall()

        return jsonify([
            format_opportunity(row) for row in rows
        ]), 200

    except Error:
        app.logger.exception("Error retrieving opportunities")
        return jsonify({"error": "Database operation failed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# 3. Retrieve one opportunity
@app.route(
    "/api/opportunities/<int:opportunity_id>",
    methods=["GET"]
)
def get_opportunity(opportunity_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM opportunities WHERE id = %s",
            (opportunity_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return jsonify({"error": "Opportunity not found."}), 404

        return jsonify(format_opportunity(row)), 200

    except Error:
        app.logger.exception("Error retrieving opportunity")
        return jsonify({"error": "Database operation failed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# 4. Update an opportunity
@app.route(
    "/api/opportunities/<int:opportunity_id>",
    methods=["PUT"]
)
def update_opportunity(opportunity_id):
    data = request.get_json(silent=True)
    error = validate_data(data)

    if error:
        return jsonify({"error": error}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM opportunities WHERE id = %s",
            (opportunity_id,)
        )

        if cursor.fetchone() is None:
            return jsonify({"error": "Opportunity not found."}), 404

        columns = list(data.keys())
        assignments = ", ".join(
            f"{column} = %s" for column in columns
        )

        sql = (
            f"UPDATE opportunities SET {assignments} "
            "WHERE id = %s"
        )

        values = [data[column] for column in columns]
        values.append(opportunity_id)

        cursor.execute(sql, tuple(values))
        connection.commit()

        return jsonify({
            "message": "Opportunity updated successfully."
        }), 200

    except Error:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Error updating opportunity")
        return jsonify({"error": "Database operation failed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# 5. Delete an opportunity
@app.route(
    "/api/opportunities/<int:opportunity_id>",
    methods=["DELETE"]
)
def delete_opportunity(opportunity_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM opportunities WHERE id = %s",
            (opportunity_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({"error": "Opportunity not found."}), 404

        connection.commit()

        return jsonify({
            "message": "Opportunity deleted successfully."
        }), 200

    except Error:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Error deleting opportunity")
        return jsonify({"error": "Database operation failed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# Start the development server
if __name__ == "__main__":
    app.run(debug=True)

import json
import os
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("students.json")


def load_students():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("Student data must be a JSON list.")
        return data
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        raise RuntimeError("Could not read students.json. Check that it contains valid JSON.") from exc


def save_students(students):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(students, file, indent=4, ensure_ascii=False)


def calculate_result(marks):
    total = sum(marks.values())
    average = total / len(marks)
    if average >= 85:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"
    return total, round(average, 2), grade


def validate_student(data, existing_id=None):
    if not isinstance(data, dict):
        return None, "Please send student information."
    student_id = str(data.get("id", "")).strip()
    name = str(data.get("name", "")).strip()
    student_class = str(data.get("class", "")).strip()
    subjects = data.get("subjects", [])
    marks_list = data.get("marks", [])

    if not student_id or not name or not student_class:
        return None, "Student ID, name, and class/semester are required."
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,30}", student_id):
        return None, "Student ID may contain letters, numbers, hyphens, and underscores."
    if not isinstance(subjects, list) or not isinstance(marks_list, list):
        return None, "Subjects and marks must be lists."
    if not subjects or len(subjects) != len(marks_list):
        return None, "Enter the same number of subjects and marks, with at least one subject."

    clean_marks = {}
    for subject, mark in zip(subjects, marks_list):
        subject = str(subject).strip()
        if not subject:
            return None, "Subject names cannot be empty."
        if subject.lower() in {item.lower() for item in clean_marks}:
            return None, f"Duplicate subject: {subject}."
        try:
            numeric_mark = float(mark)
        except (TypeError, ValueError):
            return None, f"Marks for {subject} must be numeric."
        if not 0 <= numeric_mark <= 100:
            return None, f"Marks for {subject} must be between 0 and 100."
        clean_marks[subject] = numeric_mark if not numeric_mark.is_integer() else int(numeric_mark)

    students = load_students()
    for student in students:
        if student.get("id", "").lower() == student_id.lower() and student.get("id") != existing_id:
            return None, "This Student ID already exists."

    total, average, grade = calculate_result(clean_marks)
    return {
        "id": student_id,
        "name": name,
        "class": student_class,
        "marks": clean_marks,
        "total": total,
        "average": average,
        "grade": grade,
    }, None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def get_students():
    try:
        return jsonify(load_students())
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/students", methods=["POST"])
def add_student():
    try:
        students = load_students()
        student, error = validate_student(request.get_json(silent=True))
        if error:
            return jsonify({"error": error}), 400
        students.append(student)
        save_students(students)
        return jsonify({"message": "Student added successfully.", "student": student}), 201
    except (RuntimeError, OSError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    try:
        students = load_students()
        current = next((s for s in students if s.get("id", "").lower() == student_id.lower()), None)
        if current is None:
            return jsonify({"error": "Student not found."}), 404
        data = request.get_json(silent=True) or {}
        data["id"] = current["id"]  # ID cannot be changed during update.
        student, error = validate_student(data, existing_id=current["id"])
        if error:
            return jsonify({"error": error}), 400
        index = students.index(current)
        students[index] = student
        save_students(students)
        return jsonify({"message": "Student updated successfully.", "student": student})
    except (RuntimeError, OSError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        students = load_students()
        remaining = [s for s in students if s.get("id", "").lower() != student_id.lower()]
        if len(remaining) == len(students):
            return jsonify({"error": "Student not found."}), 404
        save_students(remaining)
        return jsonify({"message": "Student deleted successfully."})
    except (RuntimeError, OSError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/ai/<kind>/<student_id>", methods=["POST"])
def student_ai(kind, student_id):
    if kind not in ("analyze", "tips"):
        return jsonify({"error": "Unknown AI request. Use analyze or tips."}), 400
    try:
        students = load_students()
        student = next((s for s in students if s.get("id", "").lower() == student_id.lower()), None)
        if student is None:
            return jsonify({"error": "Student not found."}), 404
        from ai_helper import analyze_performance, generate_study_tips
        result = analyze_performance(student) if kind == "analyze" else generate_study_tips(student)
        return jsonify({"result": result})
    except Exception as exc:
        # The AI helper returns safe, readable errors; do not expose secrets or request details.
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    import webbrowser
    from threading import Timer

    if os.getenv("AUTO_OPEN_BROWSER", "true").lower() == "true":
        Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")

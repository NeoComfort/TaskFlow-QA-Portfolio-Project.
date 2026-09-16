from __future__ import annotations

from itertools import count

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

VALID_STATUSES = {"todo", "in_progress", "done"}
task_ids = count(1)
tasks: dict[int, dict] = {}


def error(message: str, status_code: int):
    return jsonify({"error": message}), status_code


def validate_task_payload(payload: object, partial: bool = False):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."

    if not partial and "title" not in payload:
        return "title is required."

    if "title" in payload:
        title = payload["title"]
        if not isinstance(title, str) or not title.strip():
            return "title must be a non-empty string."
        if len(title.strip()) > 120:
            return "title must be 120 characters or fewer."

    if "description" in payload and not isinstance(payload["description"], str):
        return "description must be a string."

    if "status" in payload and payload["status"] not in VALID_STATUSES:
        return "status must be todo, in_progress, or done."

    return None


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def dashboard():
    return render_template("index.html")


@app.get("/tasks")
def list_tasks():
    status = request.args.get("status")
    if status and status not in VALID_STATUSES:
        return error("status must be todo, in_progress, or done.", 400)

    results = list(tasks.values())
    if status:
        results = [task for task in results if task["status"] == status]
    return jsonify(results)


@app.post("/tasks")
def create_task():
    payload = request.get_json(silent=True)
    validation_error = validate_task_payload(payload)
    if validation_error:
        return error(validation_error, 400)

    task_id = next(task_ids)
    task = {
        "id": task_id,
        "title": payload["title"].strip(),
        "description": payload.get("description", ""),
        "status": payload.get("status", "todo"),
    }
    tasks[task_id] = task
    return jsonify(task), 201


@app.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        return error("task not found.", 404)
    return jsonify(task)


@app.patch("/tasks/<int:task_id>")
def update_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        return error("task not found.", 404)

    payload = request.get_json(silent=True)
    validation_error = validate_task_payload(payload, partial=True)
    if validation_error:
        return error(validation_error, 400)

    for field in ("title", "description", "status"):
        if field in payload:
            task[field] = payload[field].strip() if field == "title" else payload[field]
    return jsonify(task)


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    if task_id not in tasks:
        return error("task not found.", 404)
    del tasks[task_id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)

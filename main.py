from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import json
from image_analysis_pipeline import process_directory
from celery_worker import run_ocr

app = Flask(__name__)
UPLOAD_FOLDER = "images"
REPORT_FILE = "forensic_reports.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_UI = """<h1>Image Forensics Dashboard</h1> ... (your UI here) ..."""

@app.route("/")
def home():
    return render_template_string(HTML_UI)

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    return jsonify({"message": f"Image '{file.filename}' uploaded successfully.", "filename": file.filename})

@app.route("/analyze", methods=["POST"])
def analyze():
    process_directory(UPLOAD_FOLDER, output_report=REPORT_FILE)
    return jsonify({"message": "Analysis complete.", "report": REPORT_FILE})

@app.route("/report", methods=["GET"])
def get_report():
    if not os.path.exists(REPORT_FILE):
        return jsonify({"error": "No report found."}), 404
    with open(REPORT_FILE, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/ocr", methods=["POST"])
def start_ocr():
    filename = request.json.get("filename")
    if not filename:
        return jsonify({"error": "Filename not provided"}), 400

    image_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    task = run_ocr.delay(image_path)
    return jsonify({"message": "OCR task started", "task_id": task.id})

@app.route("/ocr-status/<task_id>", methods=["GET"])
def ocr_status(task_id):
    task = run_ocr.AsyncResult(task_id)
    if task.state == "PENDING":
        return jsonify({"status": "pending"})
    elif task.state == "SUCCESS":
        return jsonify({"status": "success", "result": task.result})
    elif task.state == "FAILURE":
        return jsonify({"status": "failure", "error": str(task.info)})
    else:
        return jsonify({"status": task.state})

@app.route("/images/<filename>", methods=["GET"])
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

### Paste your full Flask API from Canvas here ###
from flask import Flask, request, jsonify, send_from_directory
import os
import json
from image_analysis_pipeline import process_directory

app = Flask(__name__)
UPLOAD_FOLDER = "images"
REPORT_FILE = "forensic_reports.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    return jsonify({"message": f"Image '{file.filename}' uploaded successfully."})

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

@app.route("/images/<filename>", methods=["GET"])
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

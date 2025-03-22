from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import json
from image_analysis_pipeline import process_directory

app = Flask(__name__)
UPLOAD_FOLDER = "images"
REPORT_FILE = "forensic_reports.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML UI embedded as homepage
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Image Forensics UI</title>
  <style>
    body { font-family: sans-serif; padding: 2em; max-width: 700px; margin: auto; }
    input[type="file"] { margin-bottom: 1em; }
    button { margin: 0.5em 0; padding: 0.5em 1em; }
    .preview img { max-width: 100%; margin: 1em 0; border: 1px solid #ccc; border-radius: 6px; }
    pre { background: #f4f4f4; padding: 1em; border-radius: 5px; overflow-x: auto; }
  </style>
</head>
<body>
  <h1>🔍 Image Forensics Dashboard</h1>
  <input type="file" id="imageInput" accept="image/*" />
  <br />
  <button onclick="uploadImage()">📤 Upload Image</button>
  <button onclick="runAnalysis()">🧪 Run Analysis</button>
  <button onclick="fetchReport()">📄 View Report</button>

  <div class="preview" id="preview"></div>
  <div class="report" id="report"></div>

  <script>
    const API_BASE = "";

    function uploadImage() {
      const input = document.getElementById("imageInput");
      if (!input.files.length) return alert("Please select an image");

      const formData = new FormData();
      formData.append("image", input.files[0]);

      fetch(`${API_BASE}/upload`, { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
          document.getElementById("preview").innerHTML = `<p>✅ ${data.message}</p>`;
        })
        .catch(err => alert("Upload failed"));
    }

    function runAnalysis() {
      fetch(`${API_BASE}/analyze`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
          document.getElementById("preview").innerHTML = `<p>✅ ${data.message}</p>`;
        })
        .catch(err => alert("Analysis failed"));
    }

    function fetchReport() {
      fetch(`${API_BASE}/report`)
        .then(res => res.json())
        .then(data => {
          const flagged = data.reports.filter(r => r.flagged);
          document.getElementById("report").innerHTML = `
            <h2>📄 Report</h2>
            <pre>${JSON.stringify(flagged, null, 2)}</pre>
          `;
        })
        .catch(err => alert("Could not fetch report"));
    }
  </script>
</body>
</html>
"""
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

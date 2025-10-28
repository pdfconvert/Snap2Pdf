dfrom flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile

app = Flask(__name__)
CORS(app)  # ✅ allow GitHub frontend to access Render backend

UPLOAD_FOLDER = tempfile.gettempdir()

@app.route("/")
def home():
    return jsonify({"message": "Snap2PDF Backend Running ✅"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files["file"]
    if pdf_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    tmp_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(tmp_path)

    # ✅ Here we just confirm upload success
    # (Later, OCR or analysis can be added here)
    return jsonify({
        "tmpfile": pdf_file.filename,
        "path": tmp_path,
        "message": "File uploaded successfully",
        "status": "ok"
    })

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import io, os, tempfile, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

@app.after_request
def add_cors(resp):
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    resp.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return resp

@app.route('/')
def home():
    return jsonify({"message": "Snap2Pdf Backend Running"})

@app.route('/upload', methods=['POST'])
def upload_pdf():
    f = request.files.get('file')
    if not f:
        return jsonify({"error": "no file"}), 400
    filename = secure_filename(f.filename)
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    f.save(tmp_path)
    doc = fitz.open(tmp_path)
    pages = doc.page_count
    doc.close()
    return jsonify({"tmpfile": tmp_path, "pages": pages})

@app.route('/apply_edits', methods=['POST'])
def apply_edits():
    data = request.get_json()
    tmpfile = data.get('tmpfile')
    edits = data.get('edits', [])
    if not os.path.exists(tmpfile):
        return jsonify({"error": "missing file"}), 400
    doc = fitz.open(tmpfile)
    for ed in edits:
        p = ed.get("page", 0)
        text = ed.get("text", "")
        x, y, w, h = ed.get("x"), ed.get("y"), ed.get("w"), ed.get("h")
        font = ed.get("font", "helv")
        size = ed.get("size", 12)
        color = tuple([c / 255 for c in ed.get("color", [0, 0, 0])])
        rect = fitz.Rect(x, y, x + w, y + h)
        page = doc[p]
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))  # mask old text
        page.insert_textbox(rect, text, fontsize=size, fontname=font, color=color)
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    out.seek(0)
    return send_file(out, mimetype='application/pdf', as_attachment=True, download_name='edited.pdf')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

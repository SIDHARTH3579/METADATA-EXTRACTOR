from flask import Flask, render_template, request, jsonify, send_file
from extractor import extract_metadata, strip_metadata, detect_file_type
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
CLEAN_FOLDER = "cleaned"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEAN_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Save temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    metadata = extract_metadata(file_path)
    file_type = detect_file_type(file_path)

    return jsonify({'metadata': metadata, 'type': file_type})

@app.route('/strip', methods=['POST'])
def strip():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    clean_bytes, extension = strip_metadata(file_path)
    cleaned_path = os.path.join(CLEAN_FOLDER, f"cleaned_{file.filename}")
    with open(cleaned_path, "wb") as f:
        f.write(clean_bytes)

    return send_file(
        cleaned_path,
        as_attachment=True,
        download_name=f"cleaned_{file.filename}"
    )

if __name__ == '__main__':
    app.run(debug=True)

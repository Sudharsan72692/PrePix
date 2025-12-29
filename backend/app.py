from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import io
import os

app = Flask(__name__)
CORS(app)


def process_image_file(file_stream, output_ext):
    # Read bytes into numpy array
    file_bytes = np.frombuffer(file_stream.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        return None
    # Convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Encode to requested format
    success, encoded = cv2.imencode(output_ext, gray)
    if not success:
        return None
    return io.BytesIO(encoded.tobytes())


@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    f = request.files['file']
    filename = f.filename or 'image'
    name, ext = os.path.splitext(filename)
    if ext == '':
        ext = '.png'
    output_ext = '.png' if ext.lower() not in ['.png', '.jpg', '.jpeg'] else ext
    processed_io = process_image_file(f.stream, output_ext)
    if processed_io is None:
        return jsonify({'error': 'processing failed'}), 500
    processed_io.seek(0)
    out_name = f"{name}_gray{output_ext}"
    return send_file(processed_io, as_attachment=True, download_name=out_name, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

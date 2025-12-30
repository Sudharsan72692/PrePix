from flask import Flask, request, send_file, jsonify
import base64
from flask_cors import CORS
import cv2
import numpy as np
import io
import os

app = Flask(__name__)
CORS(app,origins=[
    "https://prepix.netlify.app",
    "http://localhost:5173"
])


def process_image_file(file_stream, output_ext):
    # Read bytes into numpy array
    file_bytes = np.frombuffer(file_stream.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        return None
    # Resize to 600x400

    # Grayscale (stand-alone image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Return processed numpy arrays (gray, blur, edges) for further encoding
    # Gaussian blur (on color img)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    # Edges (use gray for better results)
    edges = cv2.Canny(img, 100, 100)

    return gray, blur, edges


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
    processed = process_image_file(f.stream, output_ext)
    if processed is None:
        return jsonify({'error': 'processing failed'}), 500

    gray, blur, edges = processed

    # Helper to encode image and return base64 data URL
    def encode_to_dataurl(img_array):
        success, encoded = cv2.imencode('.png', img_array)
        if not success:
            return None
        b64 = base64.b64encode(encoded.tobytes()).decode('ascii')
        return f"data:image/png;base64,{b64}"

    gray_url = encode_to_dataurl(gray)
    blur_url = encode_to_dataurl(blur)
    edges_url = encode_to_dataurl(edges)

    if not all([gray_url, blur_url, edges_url]):
        return jsonify({'error': 'encoding failed'}), 500

    return jsonify({
        'gray': gray_url,
        'blur': blur_url,
        'edges': edges_url,
        'gray_name': f"{name}_gray.png",
        'blur_name': f"{name}_blur.png",
        'edges_name': f"{name}_edges.png",
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

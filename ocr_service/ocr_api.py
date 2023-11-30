from io import BytesIO

import pytesseract
from flask import Flask, jsonify, request
from PIL import Image

app = Flask(__name__)

exts = Image.registered_extensions()
ALLOWED_EXTENSIONS = {ex for ex, f in exts.items() if f in Image.OPEN and f in Image.SAVE}


def allowed_file(filename):
    return '.' in filename and filename[filename.rfind('.'):].lower() in ALLOWED_EXTENSIONS

@app.route('/perform_ocr', methods=['POST'])
def perform_ocr():
    try:
        # Check if the post request has the image
        if 'image' not in request.files:
            return jsonify({"message": "Data posted does not contain an image"}), 400
        
        file = request.files['image']

        # Check if the image is empty
        if file.filename == '':
            return jsonify({"message": "No image file uploaded"}), 400
        
        # Check if the file type is supported
        if not allowed_file(file.filename):
            return jsonify({"message": "Unsupported media type. Please upload a supported image file"}), 415
        
        # Process the file
        image_data = BytesIO(file.read())
        text = pytesseract.image_to_string(Image.open(image_data))
        text = text.replace("\n", " ")
        
        # Check if the image contains text
        if text:
            return jsonify({"text": text, "message": "OCR processing successful"}), 200
        return jsonify({"message": "Unable to extract text from the image"}), 400

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
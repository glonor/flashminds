from io import BytesIO

import pytesseract
from flask import Flask, jsonify, request
from PIL import Image

app = Flask(__name__)

exts = Image.registered_extensions()
ALLOWED_EXTENSIONS = {ex for ex, f in exts.items() if f in Image.OPEN and f in Image.SAVE}


def allowed_file(filename):
    return '.' in filename and filename[filename.rfind('.'):].lower() in ALLOWED_EXTENSIONS

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        # Check if the post request has the image
        if 'image' not in request.files:
            return jsonify({"message": "Data posted does not contain an image"}), 400
        
        file = request.files['image']
        
        # Check if the file type is supported
        if not allowed_file(file.filename):
            return jsonify({"message": "The file type you uploaded is not supported"}), 400
        
        # Process the file
        if file and allowed_file(file.filename):
            image_data = BytesIO(file.read())
            text = pytesseract.image_to_string(Image.open(image_data))
            text = text.replace("\n", " ")
            return jsonify({"text": text}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error reviewing flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# Start Application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
import os
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

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
            filename = file.filename.lower()
            image_file = os.path.join(UPLOAD_FOLDER, filename)
            file.save(image_file)
            text = pytesseract.image_to_string(Image.open(image_file))
            return jsonify({"text": text}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error reviewing flashcard: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

# Start Application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
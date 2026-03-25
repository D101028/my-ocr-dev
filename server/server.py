import os
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import configparser

config = configparser.ConfigParser()
config.read('config.conf')
default_section = config["DEFAULT"]

# filepath: /mnt/d/Projects/paddleocr-dev/server.py

app = Flask(__name__)

# Initialize PaddleOCR instance
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

@app.route('/ocr', methods=['POST'])
def perform_ocr():
    """
    OCR endpoint that accepts image file or image path
    """
    try:
        if 'file' in request.files:
            # Handle file upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            file.save('temp_image.png')
            filename = 'temp_image.png'
        elif 'path' in request.json:
            # Handle file path
            filename = request.json['path']
        else:
            return jsonify({'error': 'No file or path provided'}), 400
        
        # Run OCR inference
        result = ocr.predict(filename)
        
        # Format response
        response_data = {
            'input_path': filename,
            'rec_texts': [],
            # 'rec_scores': [],
            # 'rec_boxes': []
        }
        
        for line in result:
            response_data['rec_texts'] += line['rec_texts']
            # response_data['rec_scores'] += line['rec_scores']
            # response_data['rec_boxes'] += line['rec_boxes']
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host=default_section.get("HOST"), port=int(default_section.get("PORT", 5000)))


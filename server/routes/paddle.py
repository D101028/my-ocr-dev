import os
import shutil
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from flask import Blueprint, request, jsonify
from paddleocr import PaddleOCR

from config import Config

paddle_bp = Blueprint('paddle', __name__)

# Initialize PaddleOCR instance
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

@paddle_bp.route(Config.PADDLE_OCR_ROUTE, methods=['POST'])
def perform_ocr():
    """
    OCR endpoint that accepts image file or image path
    """
    TEMP_WORKING_DIR = os.path.join(Config.TEMP_DIR, os.urandom(8).hex())
    if not os.path.isdir(TEMP_WORKING_DIR):
        os.mkdir(TEMP_WORKING_DIR)
    try:
        if 'file' in request.files:
            # Handle file upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            filename = os.path.join(TEMP_WORKING_DIR, f'{os.urandom(8).hex()}.png')
            file.save(filename)
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

    finally:
        shutil.rmtree(TEMP_WORKING_DIR)


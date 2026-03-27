import os

from flask import Blueprint, request, jsonify
from texify.inference import batch_inference
from texify.model.model import load_model
from texify.model.processor import load_processor
from PIL import Image

from config import Config

tex_bp = Blueprint('tex', __name__)

# Initialize texify model and processor
model = load_model()
processor = load_processor()

@tex_bp.route(Config.TEXIFY_ROUTE, methods=['POST'])
def perform_ocr():
    """
    Texify endpoint that accepts image file or image path
    Converts mathematical expressions and formulas in images to LaTeX
    """
    try:
        if 'file' in request.files:
            # Handle file upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            filename = os.path.join(Config.WORKING_DIR, f'{os.urandom(8).hex()}.png')
            file.save(filename)
        elif 'path' in request.json:
            # Handle file path
            filename = request.json['path']
        else:
            return jsonify({'error': 'No file or path provided'}), 400
        
        # Open image and run texify inference
        img = Image.open(filename)
        results = batch_inference([img], model, processor)
        
        # Format response
        response_data = {
            'input_path': filename,
            'rec_texts': results
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


import logging
import os

from flask import Flask, jsonify
from waitress import serve

from config import Config
from routes import *

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session encryption

# Register blueprints
app.register_blueprint(paddle_bp)
app.register_blueprint(tex_bp)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info(f">> Starting Server on {Config.HOST}:{Config.PORT} <<")
    serve(app, host=Config.HOST, port=Config.PORT)




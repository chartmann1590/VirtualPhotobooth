import os
import io
import base64
import time
from datetime import datetime
from typing import List
from flask import Blueprint, current_app, render_template, request, jsonify, send_from_directory
from PIL import Image

from ..utils.settings_store import SettingsStore

bp = Blueprint('photobooth', __name__)


def _list_frames(folder: str) -> List[str]:
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.lower().endswith('.png')]


@bp.get('/')
def index():
    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    frames = _list_frames(current_app.config['UPLOAD_FOLDER'])
    return render_template('photobooth.html', frames=frames, settings=settings)


@bp.post('/api/upload_photo')
def upload_photo():
    # Receives base64 image from client
    data_url = request.json.get('image')
    frame_name = request.json.get('frame')
    if not data_url or not frame_name:
        return jsonify({"error": "Missing image or frame"}), 400

    header, encoded = data_url.split(',', 1)
    image_bytes = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(image_bytes)).convert('RGBA')

    # Composite with selected frame server-side to ensure consistency
    frame_path = os.path.join(current_app.config['UPLOAD_FOLDER'], frame_name)
    if os.path.exists(frame_path):
        frame_img = Image.open(frame_path).convert('RGBA')
        frame_img = frame_img.resize(image.size, Image.LANCZOS)
        image = Image.alpha_composite(image, frame_img)

    # Save photo
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"photo_{ts}.png"
    save_path = os.path.join(current_app.config['PHOTOS_FOLDER'], filename)
    image.save(save_path, format='PNG')

    return jsonify({"filename": filename})


@bp.get('/photos/<path:filename>')
def get_photo(filename: str):
    return send_from_directory(current_app.config['PHOTOS_FOLDER'], filename)

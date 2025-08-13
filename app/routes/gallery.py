import os
from typing import List
from flask import Blueprint, current_app, render_template, jsonify, request, url_for

from ..utils.settings_store import SettingsStore
from ..services.email_service import send_email_smtp
from ..services.sms_service import SMSGateClient

bp = Blueprint('gallery', __name__)


def _list_photos(folder: str) -> List[str]:
    if not os.path.exists(folder):
        return []
    return sorted([f for f in os.listdir(folder) if f.lower().endswith('.png') or f.lower().endswith('.jpg')])


@bp.get('/gallery')
def gallery():
    photos = _list_photos(current_app.config['PHOTOS_FOLDER'])
    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    return render_template('gallery.html', photos=photos, settings=settings)


@bp.post('/api/share/email')
def share_email():
    data = request.json or {}
    filename = data.get('filename')
    to_email = data.get('email')
    if not filename or not to_email:
        return jsonify({"error": "Missing filename or email"}), 400

    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    photo_path = os.path.join(current_app.config['PHOTOS_FOLDER'], filename)

    try:
        send_email_smtp(
            host=settings['smtp']['host'],
            port=int(settings['smtp']['port']),
            user=settings['smtp']['user'],
            password=settings['smtp']['password'],
            from_email=settings['smtp']['from_email'] or settings['smtp']['user'],
            to_email=to_email,
            subject='Your PhotoBooth Photo',
            body='Attached is your photobooth photo. Have fun!',
            attachment_path=photo_path,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"ok": True})


@bp.post('/api/share/sms')
def share_sms():
    data = request.json or {}
    filename = data.get('filename')
    phone = data.get('phone')
    if not filename or not phone:
        return jsonify({"error": "Missing filename or phone"}), 400

    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    # Send direct link to the photo
    photo_url = request.host_url.rstrip('/') + url_for('photobooth.get_photo', filename=filename)
    message = f"Your photobooth photo: {photo_url}"

    try:
        client = SMSGateClient(
            api_base=settings['sms']['api_base'],
            username=settings['sms']['username'],
            password=settings['sms']['password'],
        )
        client.send_sms(message=message, phone_numbers=[phone])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"ok": True})

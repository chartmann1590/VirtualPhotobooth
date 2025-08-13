import os
from typing import Any, Dict
from flask import Blueprint, current_app, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename

from ..utils.settings_store import SettingsStore
from ..utils.security import check_admin_password, ensure_csrf_token, validate_csrf

bp = Blueprint('settings', __name__)

ALLOWED_FRAME_EXTENSIONS = {'.png'}


def is_logged_in() -> bool:
    return session.get('is_admin') is True


@bp.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('settings.settings_page'))


@bp.route('/settings', methods=['GET', 'POST'])
def settings_page():
    store = SettingsStore(current_app.config['SETTINGS_PATH'])

    # Inline login handling
    if request.method == 'POST' and not is_logged_in() and 'password' in request.form:
        validate_csrf()
        password = request.form.get('password', '')
        if check_admin_password(password):
            session['is_admin'] = True
            return redirect(url_for('settings.settings_page'))
        frames = [f for f in os.listdir(current_app.config['UPLOAD_FOLDER']) if f.lower().endswith('.png')]
        return render_template('settings.html', settings=store.read(), frames=frames, csrf_token=ensure_csrf_token(), login_error='Invalid password', is_admin=False)

    # Settings save (only when logged in)
    if request.method == 'POST' and is_logged_in():
        validate_csrf()
        data = store.read()
        data['smtp']['host'] = request.form.get('smtp_host', '')
        data['smtp']['port'] = int(request.form.get('smtp_port', '587') or 587)
        data['smtp']['user'] = request.form.get('smtp_user', '')
        data['smtp']['password'] = request.form.get('smtp_password', '')
        data['smtp']['from_email'] = request.form.get('smtp_from', '')
        data['sms']['api_base'] = request.form.get('sms_api_base', 'https://api.sms-gate.app')
        data['sms']['username'] = request.form.get('sms_username', '')
        data['sms']['password'] = request.form.get('sms_password', '')
        data['tts']['enabled'] = request.form.get('tts_enabled') == 'on'
        data['tts']['engine'] = request.form.get('tts_engine', data['tts'].get('engine', 'browser'))
        data['tts']['voice'] = request.form.get('tts_voice', 'default')
        data['tts']['prompt'] = request.form.get('tts_prompt', 'Get ready! The photo will start soon.')
        data['tts']['piper_model'] = request.form.get('piper_model', data['tts'].get('piper_model', '/app/piper/models/en_US-amy-low.onnx'))
        store.write(data)

        if 'frame' in request.files:
            file = request.files['frame']
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext in ALLOWED_FRAME_EXTENSIONS:
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(save_path)

        return redirect(url_for('settings.settings_page'))

    frames = [f for f in os.listdir(current_app.config['UPLOAD_FOLDER']) if f.lower().endswith('.png')]
    return render_template('settings.html', settings=store.read(), frames=frames, csrf_token=ensure_csrf_token(), is_admin=is_logged_in())


@bp.post('/api/delete_frame')
def delete_frame():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    validate_csrf()
    filename = request.form.get('filename')
    if not filename:
        return jsonify({"error": "Missing filename"}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return jsonify({"ok": True})

import io
import requests
from flask import Blueprint, current_app, jsonify, request, Response

from ..utils.settings_store import SettingsStore

bp = Blueprint('tts', __name__)


def _get_opentts_base() -> str:
    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    url = settings.get('tts', {}).get('opentts_url', 'http://opentts:5500')
    return url.rstrip('/')


@bp.get('/api/tts/voices')
def list_voices():
    base = _get_opentts_base()
    try:
        r = requests.get(f"{base}/api/voices", timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@bp.get('/api/tts/speak')
def tts_speak():
    text = request.args.get('text') or 'Hello'
    voice = request.args.get('voice') or 'en_US/m-ailabs_low#male-en-0'
    base = _get_opentts_base()
    params = {
        'text': text,
        'voice': voice,
        'format': 'audio/mpeg'
    }
    try:
        r = requests.get(f"{base}/api/tts", params=params, stream=True, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    def generate():
        try:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        finally:
            r.close()

    return Response(generate(), content_type=r.headers.get('Content-Type', 'audio/mpeg'))



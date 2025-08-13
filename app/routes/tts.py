import io
import os
import subprocess
import tempfile
import requests
from flask import Blueprint, current_app, jsonify, request, Response, send_file

from ..utils.settings_store import SettingsStore

bp = Blueprint('tts', __name__)


def _get_piper_model() -> str:
    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    return settings.get('tts', {}).get('piper_model', '/app/piper/models/en_US-amy-low.onnx')


@bp.get('/api/tts/voices')
def list_voices():
    # For piper, list pre-bundled models mounted in /app/piper/models (filenames)
    models_dir = '/app/piper/models'
    try:
        files = []
        for root, _, fs in os.walk(models_dir):
            for f in fs:
                if f.endswith('.onnx'):
                    files.append(os.path.join(root, f).replace(models_dir + '/', ''))
        return jsonify({"voices": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get('/api/tts/speak')
def tts_speak():
    text = request.args.get('text') or 'Hello'
    model_rel = request.args.get('voice') or None
    model_path = os.path.join('/app/piper/models', model_rel) if model_rel else _get_piper_model()
    # Use piper CLI to synthesize to WAV, then convert to MP3 with ffmpeg if available, else return WAV
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpwav:
            wav_path = tmpwav.name
        cmd = [
            'piper',
            '--model', model_path,
            '--output_file', wav_path,
            '--text', text
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Try to transcode to mp3 if ffmpeg exists
        mp3_path = wav_path.replace('.wav', '.mp3')
        try:
            subprocess.run(['ffmpeg', '-y', '-i', wav_path, '-codec:a', 'libmp3lame', mp3_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.remove(wav_path)
            return send_file(mp3_path, mimetype='audio/mpeg', as_attachment=False, download_name='speech.mp3')
        except Exception:
            return send_file(wav_path, mimetype='audio/wav', as_attachment=False, download_name='speech.wav')
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr.decode('utf-8', errors='ignore')}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500



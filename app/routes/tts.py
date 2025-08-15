import io
import os
import time
import requests
import urllib.parse
from flask import Blueprint, current_app, jsonify, request, Response, send_file
import logging

from ..utils.settings_store import SettingsStore

bp = Blueprint('tts', __name__)
logger = logging.getLogger(__name__)

# Free TTS service configurations
TTS_SERVICES = {
    'google': {
        'name': 'Google Translate TTS',
        'url': 'https://translate.google.com/translate_tts',
        'params': {
            'ie': 'UTF-8',
            'q': '',  # text
            'tl': 'en',  # language
            'client': 'tw-ob'
        }
    },
    'microsoft': {
        'name': 'Microsoft Cognitive Services TTS',
        'url': 'https://eastus.tts.speech.microsoft.com/cognitiveservices/v1',
        'headers': {
            'Ocp-Apim-Subscription-Key': '',  # Will be set from settings
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
        },
        'api_key_required': True
    },
    'elevenlabs': {
        'name': 'ElevenLabs (Free Tier)',
        'url': 'https://api.elevenlabs.io/v1/text-to-speech',
        'headers': {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json'
        },
        'api_key_required': True
    }
}

# Available voices for each service
TTS_VOICES = {
    'google': [
        {'id': 'en', 'name': 'English', 'gender': 'neutral'},
        {'id': 'es', 'name': 'Spanish', 'gender': 'neutral'},
        {'id': 'fr', 'name': 'French', 'gender': 'neutral'},
        {'id': 'de', 'name': 'German', 'gender': 'neutral'},
        {'id': 'it', 'name': 'Italian', 'gender': 'neutral'},
        {'id': 'pt', 'name': 'Portuguese', 'gender': 'neutral'},
        {'id': 'ru', 'name': 'Russian', 'gender': 'neutral'},
        {'id': 'ja', 'name': 'Japanese', 'gender': 'neutral'},
        {'id': 'ko', 'name': 'Korean', 'gender': 'neutral'},
        {'id': 'zh', 'name': 'Chinese', 'gender': 'neutral'}
    ],
    'microsoft': [
        {'id': 'en-US-JennyNeural', 'name': 'Jenny (US English)', 'gender': 'female'},
        {'id': 'en-US-GuyNeural', 'name': 'Guy (US English)', 'gender': 'male'},
        {'id': 'en-GB-SoniaNeural', 'name': 'Sonia (UK English)', 'gender': 'female'},
        {'id': 'en-GB-RyanNeural', 'name': 'Ryan (UK English)', 'gender': 'male'},
        {'id': 'es-ES-ElviraNeural', 'name': 'Elvira (Spanish)', 'gender': 'female'},
        {'id': 'es-ES-AlvaroNeural', 'name': 'Alvaro (Spanish)', 'gender': 'male'},
        {'id': 'fr-FR-DeniseNeural', 'name': 'Denise (French)', 'gender': 'female'},
        {'id': 'fr-FR-HenriNeural', 'name': 'Henri (French)', 'gender': 'male'},
        {'id': 'de-DE-KatjaNeural', 'name': 'Katja (German)', 'gender': 'female'},
        {'id': 'de-DE-ConradNeural', 'name': 'Conrad (German)', 'gender': 'male'},
        {'id': 'it-IT-IsabellaNeural', 'name': 'Isabella (Italian)', 'gender': 'female'},
        {'id': 'it-IT-DiegoNeural', 'name': 'Diego (Italian)', 'gender': 'male'},
        {'id': 'zh-CN-XiaoxiaoNeural', 'name': 'Xiaoxiao (Chinese)', 'gender': 'female'},
        {'id': 'zh-CN-YunxiNeural', 'name': 'Yunxi (Chinese)', 'gender': 'male'},
        {'id': 'ja-JP-NanamiNeural', 'name': 'Nanami (Japanese)', 'gender': 'female'},
        {'id': 'ja-JP-KeitaNeural', 'name': 'Keita (Japanese)', 'gender': 'male'},
        {'id': 'ko-KR-SunHiNeural', 'name': 'SunHi (Korean)', 'gender': 'female'},
        {'id': 'ko-KR-InJoonNeural', 'name': 'InJoon (Korean)', 'gender': 'male'},
        {'id': 'ru-RU-SvetlanaNeural', 'name': 'Svetlana (Russian)', 'gender': 'female'},
        {'id': 'ru-RU-DmitryNeural', 'name': 'Dmitry (Russian)', 'gender': 'male'}
    ],
    'elevenlabs': [
        {'id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Rachel (English)', 'gender': 'female'},
        {'id': 'AZnzlk1XvdvUeBnXmlld', 'name': 'Domi (English)', 'gender': 'female'},
        {'id': 'EXAVITQu4vr4xnSDxMaL', 'name': 'Bella (English)', 'gender': 'female'},
        {'id': 'ErXwobaYiN1PXXYv6Ewj', 'name': 'Josh (English)', 'gender': 'male'},
        {'id': 'MF3mGyEYCl7XYWbV9V6O', 'name': 'Elli (English)', 'gender': 'female'},
        {'id': 'TxGEqnHWrfWFTfGW9XjX', 'name': 'Adam (English)', 'gender': 'male'},
        {'id': 'VR6AewLTigWG4xSOukaG', 'name': 'Sam (English)', 'gender': 'male'}
    ]
}

@bp.get('/api/tts/voices')
def list_voices():
    """List available voices for the selected TTS service"""
    service = request.args.get('service', 'google')
    
    if service not in TTS_VOICES:
        return jsonify({"error": f"Unknown service: {service}"}), 400
    
    voices = TTS_VOICES[service]
    return jsonify({
        "service": service,
        "service_name": TTS_SERVICES[service]['name'],
        "voices": voices
    })

@bp.get('/api/tts/speak')
def tts_speak():
    """Generate speech using the selected TTS service"""
    text = request.args.get('text', 'Hello')
    service = request.args.get('service', 'google')
    voice = request.args.get('voice', '')
    
    if not text:
        return jsonify({"error": "Text parameter is required"}), 400
    
    if service not in TTS_SERVICES:
        return jsonify({"error": f"Unknown service: {service}"}), 400
    
    logger.info(f"TTS request: service={service}, voice={voice}, text_length={len(text)}")
    
    try:
        if service == 'google':
            return _google_tts(text, voice)
        elif service == 'microsoft':
            return _microsoft_tts(text, voice)
        elif service == 'elevenlabs':
            return _elevenlabs_tts(text, voice)
        else:
            return jsonify({"error": f"Unsupported service: {service}"}), 400
            
    except Exception as e:
        logger.error(f"TTS error for {service}: {str(e)}")
        return jsonify({"error": f"TTS service error: {str(e)}"}), 500

def _google_tts(text: str, voice: str) -> Response:
    """Generate speech using Google Translate TTS"""
    # Clean and truncate text (Google has limits)
    clean_text = text[:200]  # Google limit
    
    params = TTS_SERVICES['google']['params'].copy()
    params['q'] = clean_text
    params['tl'] = voice if voice else 'en'
    
    url = TTS_SERVICES['google']['url']
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code != 200:
        logger.error(f"Google TTS error: {response.status_code}")
        return jsonify({"error": "Google TTS service unavailable"}), 503
    
    # Google returns MP3 directly
    return Response(
        response.content,
        mimetype='audio/mpeg',
        headers={'Content-Disposition': 'inline; filename=speech.mp3'}
    )

def _microsoft_tts(text: str, voice: str) -> Response:
    """Generate speech using Microsoft Cognitive Services TTS"""
    # Get API key from settings
    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    api_key = settings.get('tts', {}).get('microsoft_api_key', '')
    
    if not api_key:
        logger.error("Microsoft TTS API key not configured")
        return jsonify({"error": "Microsoft TTS API key required"}), 400
    
    # Clean text and create SSML
    clean_text = text[:500]  # Microsoft limit
    
    # Create SSML with the selected voice
    ssml = f"""<speak version='1.0' xml:lang='en-US'>
        <voice xml:lang='en-US' xml:gender='neutral' name='{voice}'>
            {clean_text}
        </voice>
    </speak>"""
    
    url = TTS_SERVICES['microsoft']['url']
    headers = TTS_SERVICES['microsoft']['headers'].copy()
    headers['Ocp-Apim-Subscription-Key'] = api_key
    
    try:
        response = requests.post(url, data=ssml, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Microsoft TTS error: {response.status_code} - {response.text}")
            return jsonify({"error": "Microsoft TTS service error"}), 503
        
        # Microsoft returns MP3 directly
        return Response(
            response.content,
            mimetype='audio/mpeg',
            headers={'Content-Disposition': 'inline; filename=speech.mp3'}
        )
    except Exception as e:
        logger.error(f"Microsoft TTS request failed: {str(e)}")
        return jsonify({"error": "Microsoft TTS service unavailable"}), 503

def _elevenlabs_tts(text: str, voice: str) -> Response:
    """Generate speech using ElevenLabs API (requires API key)"""
    settings = SettingsStore(current_app.config['SETTINGS_PATH']).read()
    api_key = settings.get('tts', {}).get('elevenlabs_api_key', '')
    
    if not api_key:
        logger.error("ElevenLabs API key not configured")
        return jsonify({"error": "ElevenLabs API key required"}), 400
    
    # Clean text
    clean_text = text[:2500]  # ElevenLabs limit
    
    # Use default voice if none specified
    if not voice:
        voice = '21m00Tcm4TlvDq8ikWAM'  # Rachel
    
    url = f"{TTS_SERVICES['elevenlabs']['url']}/{voice}"
    headers = TTS_SERVICES['elevenlabs']['headers'].copy()
    headers['xi-api-key'] = api_key
    
    data = {
        "text": clean_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=30)
    
    if response.status_code != 200:
        logger.error(f"ElevenLabs TTS error: {response.status_code} - {response.text}")
        return jsonify({"error": "ElevenLabs TTS service error"}), 503
    
    # ElevenLabs returns MP3 directly
    return Response(
        response.content,
        mimetype='audio/mpeg',
        headers={'Content-Disposition': 'inline; filename=speech.mp3'}
    )

@bp.get('/api/tts/services')
def list_services():
    """List available TTS services"""
    services = []
    for key, service in TTS_SERVICES.items():
        services.append({
            'id': key,
            'name': service['name'],
            'api_key_required': service.get('api_key_required', False)
        })
    return jsonify({"services": services})



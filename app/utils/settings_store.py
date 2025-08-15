import json
import os
from typing import Any, Dict


DEFAULT_SETTINGS: Dict[str, Any] = {
    "smtp": {
        "host": os.getenv('SMTP_HOST', ''),
        "port": int(os.getenv('SMTP_PORT', '587') or 587),
        "user": os.getenv('SMTP_USER', ''),
        "password": os.getenv('SMTP_PASSWORD', ''),
        "from_email": os.getenv('SMTP_FROM', ''),
        "use_tls": True,
    },
    "sms": {
        "api_base": os.getenv('SMS_GATE_API_BASE', 'https://api.sms-gate.app'),
        "username": os.getenv('SMS_GATE_USERNAME', ''),
        "password": os.getenv('SMS_GATE_PASSWORD', ''),
    },
    "tts": {
        "enabled": True,
        "engine": os.getenv('TTS_ENGINE', 'google'),  # 'google', 'microsoft', 'elevenlabs', or 'browser'
        "service": os.getenv('TTS_SERVICE', 'google'),  # 'google', 'microsoft', 'elevenlabs'
        "voice": "en",  # Default voice for the selected service
        "prompt": "Get ready! The photo will start soon.",
        "elevenlabs_api_key": os.getenv('ELEVENLABS_API_KEY', ''),  # API key for ElevenLabs
        "microsoft_api_key": os.getenv('MICROSOFT_TTS_API_KEY', '')  # API key for Microsoft TTS
    },
    "ollama": {
        "enabled": False,
        "url": os.getenv('OLLAMA_URL', 'http://localhost:11434'),  # Remote Ollama URL
        "model": os.getenv('OLLAMA_MODEL', 'llama3.2'),  # Default model
        "api_key": os.getenv('OLLAMA_API_KEY', '')  # API key if required
    }
}


class SettingsStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_exists()

    def _ensure_exists(self) -> None:
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2)

    def read(self) -> Dict[str, Any]:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = DEFAULT_SETTINGS
        # Merge defaults for new keys
        merged = DEFAULT_SETTINGS.copy()
        for k, v in data.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k].update(v)
            else:
                merged[k] = v
        return merged

    def write(self, data: Dict[str, Any]) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

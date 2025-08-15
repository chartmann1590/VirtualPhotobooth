# Virtual Photobooth (Flask)

A beautifully designed, modular Flask photobooth app.

## Documentation

- [Overview](./docs/overview.md) - Project overview and architecture
- [Quick Start](./docs/quickstart.md) - Get up and running quickly
- [Configuration](./docs/configuration.md) - Environment variables and settings
- [Frames](./docs/frames.md) - Adding and managing photobooth frames
- [Text-to-Speech](./docs/tts.md) - TTS setup and configuration
- [Ollama AI](./docs/ollama.md) - AI-powered prompt generation
- [Email & SMTP](./docs/email_smtp.md) - Email configuration
- [SMS Gateway](./docs/sms_gateway.md) - SMS setup and configuration
- [Docker Deployment](./docs/deployment_docker.md) - Container deployment guide
- [Operations](./docs/operations.md) - Running and maintaining the application

## Highlights
- Photobooth page with selectable frames, camera capture, 3-second countdown, and optional TTS guidance
- Admin Settings page (password from `.env`) to manage frames, SMTP, SMS Gateway, and TTS settings
- Gallery page to view and share captured photos via Email or SMS

## Quick Start

1. Create and fill `.env` in project root:

```
FLASK_ENV=development
SECRET_KEY=replace-with-a-random-string
ADMIN_PASSWORD=replace-with-a-strong-password
# SMTP settings
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=photobooth@example.com

# SMS Gate (https://sms-gate.app/)
SMS_GATE_USERNAME=your-username
SMS_GATE_PASSWORD=your-password
SMS_GATE_API_BASE=https://api.sms-gate.app

# Optional: App port
PORT=5000
```

2. Create a virtual environment and install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the app:

```
flask --app app run --host 0.0.0.0 --port ${PORT:-5000}
```

4. Open the app:
- Photobooth: http://localhost:5000/
- Gallery: http://localhost:5000/gallery
- Settings (admin): http://localhost:5000/settings

## Quick Deploy (Docker)

1) Make the script executable and run it:
```bash
chmod +x deploy.sh
./deploy.sh
```
The script will:
- Pull the latest repo (and stop if deploy.sh changed)
- Ensure `.env` (option to keep existing)
- Generate a self-signed TLS cert
- Build and start containers (web + nginx + optional piper)
- Auto-download a small set of Piper models for common locales (male/female when available)
- Print your system IP to open: `https://<your-ip>/`

2) TTS configuration: see [Text-to-Speech](./docs/tts.md)

## Frames
Upload transparent PNG frames via Settings. The camera view is masked to the transparent area of the frame. Place PNGs into `static/frames/`.

## Tech Notes
- Backend: Flask, modular Blueprints
- Storage: Local `photos/` directory; app settings persisted to `config/settings.json`
- Email: SMTP via `smtplib`
- SMS: SMSGate REST API (`/3rdparty/v1/message`) with Basic Auth
- TTS: Browser Web Speech API, Google Translate TTS, Microsoft Edge TTS, and ElevenLabs (free tier)

## Security
- Admin Settings protected by password (`ADMIN_PASSWORD`)
- CSRF protection via per-session token stored in cookie and validated on POST
- Uploaded frames validated for extension and size

## License
Apache-2.0

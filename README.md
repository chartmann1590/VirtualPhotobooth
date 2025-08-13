# Virtual Photobooth (Flask)

A beautifully designed, modular Flask photobooth app.

## Table of Contents
- [Overview](./docs/overview.md)
- [Quickstart](./docs/quickstart.md)
- [Configuration](./docs/configuration.md)
- [Frames](./docs/frames.md)
- [Photobooth UX & TTS](./docs/tts.md)
- [Email (SMTP) Setup](./docs/email_smtp.md)
- [SMS (SMSGate) Setup](./docs/sms_gateway.md)
- [Deployment (Docker)](./docs/deployment_docker.md)
- [Operations](./docs/operations.md)
- [Security](./SECURITY.md)
- [License](./LICENSE)

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

## Frames
Upload transparent PNG frames via Settings. The camera view is masked to the transparent area of the frame. Place PNGs into `static/frames/`.

## Tech Notes
- Backend: Flask, modular Blueprints
- Storage: Local `photos/` directory; app settings persisted to `config/settings.json`
- Email: SMTP via `smtplib`
- SMS: SMSGate REST API (`/3rdparty/v1/message`) with Basic Auth
- TTS: Browser Web Speech API (free, offline capable in many browsers)

## Security
- Admin Settings protected by password (`ADMIN_PASSWORD`)
- CSRF protection via per-session token stored in cookie and validated on POST
- Uploaded frames validated for extension and size

## License
Apache-2.0

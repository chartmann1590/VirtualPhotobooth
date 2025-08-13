# Overview

Virtual Photobooth is a Flask-based web application for capturing photos via a webcam with customizable PNG frame overlays, offering a TTS-guided countdown, and sharing via Email (SMTP) or SMS using SMSGate.

- Photobooth page: live camera preview, frame selection, 3-second countdown, capture, and share
- Settings page: admin login (password from `.env`), upload frames, manage SMTP, SMS, and TTS
- Gallery page: view all photos, share via Email/SMS
- Data: settings stored in `config/settings.json`, photos in `photos/`, frames in `static/frames/`
- TTS: browser-based (Web Speech API)
- Deployment: Docker with Nginx reverse proxy and self-signed TLS

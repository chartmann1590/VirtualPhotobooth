# Configuration

Configuration values come from two places:
- `.env` file: one-time environment defaults for secrets and initial settings
- `config/settings.json`: runtime settings persisted by the Settings page

## .env keys

- `FLASK_ENV`: development or production
- `SECRET_KEY`: Flask secret key (random string)
- `ADMIN_PASSWORD`: Password for Settings page login

- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP port (e.g., 587)
- `SMTP_USER`: SMTP auth username
- `SMTP_PASSWORD`: SMTP auth password
- `SMTP_FROM`: From email address (defaults to `SMTP_USER` if blank)

- `SMS_GATE_USERNAME`: SMSGate username
- `SMS_GATE_PASSWORD`: SMSGate password
- `SMS_GATE_API_BASE`: Base URL for API (default `https://api.sms-gate.app`)

- `PORT`: Local Flask port for dev

## settings.json keys

- `smtp`: `host`, `port`, `user`, `password`, `from_email`, `use_tls`
- `sms`: `api_base`, `username`, `password`
- `tts`: `enabled`, `voice`, `prompt`

The app merges `.env` defaults into `settings.json` on first run.

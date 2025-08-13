# Security Policy

## Supported Versions
This project is provided as-is. Security updates are best-effort.

## Reporting a Vulnerability
If you discover a security vulnerability:
- Do not create a public issue with exploit details
- Email the maintainer privately (replace with your email)
- Provide steps to reproduce and any logs or screenshots

## Hardening Guidance
- Set a strong `ADMIN_PASSWORD` in `.env`
- Rotate SMTP/SMSGate credentials periodically
- Run behind a trusted reverse proxy and TLS (provided via Nginx)
- Limit access to the Settings page network-wise where possible
- Back up `photos/` and `config/settings.json` securely

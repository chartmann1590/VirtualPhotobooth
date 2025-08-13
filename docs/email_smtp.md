# Email (SMTP) Setup

The app sends emails with the captured photo as an attachment via SMTP.

## Prerequisites
- An SMTP provider (e.g., Gmail, SendGrid, SES, your ISP)
- Credentials: host, port (usually 587), username, password, and a from address

## Configure via Settings page
1. Open Settings: `/settings`
2. In the SMTP section, fill:
   - Host, Port, User, Password, From
3. Save Settings

Alternatively, set defaults in `.env`:
```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=your-password
SMTP_FROM=photobooth@example.com
```

## Testing
- From Photobooth: take a photo and enter your email to send
- From Gallery: enter an email per photo and send

## Troubleshooting
- Check your provider’s SMTP logs
- Some providers require app passwords (e.g., Gmail) or TLS/STARTTLS on port 587
- Ensure `SMTP_FROM` is a valid/sender-verified address
- Review app logs and exceptions

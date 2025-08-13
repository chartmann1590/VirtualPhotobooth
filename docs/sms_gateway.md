# SMS (SMSGate) Setup

We integrate with SMSGate to send SMS containing a link to the photo.

SMSGate is an open-source gateway that uses your Android device to send messages and provides a hosted API. See docs at `https://sms-gate.app/`.

## Prerequisites
- Android device with the SMSGate app installed
- Credentials (username/password) from the app home screen

## Configure in the app
1. Open Settings: `/settings`
2. In the SMS Gateway section, provide:
   - API Base: `https://api.sms-gate.app` (default)
   - Username: from the app
   - Password: from the app
3. Save Settings

Defaults can be set via `.env`:
```
SMS_GATE_USERNAME=your-username
SMS_GATE_PASSWORD=your-password
SMS_GATE_API_BASE=https://api.sms-gate.app
```

## How sending works
- We call `POST /3rdparty/v1/message` with Basic Auth and JSON payload:
```
{
  "message": "Your photobooth photo: <url>",
  "phoneNumbers": ["+15551234567"]
}
```
- On success, a 2xx status is returned.

## Testing
- Use a real phone number (+countrycode) to receive SMS
- Verify your Android device has network/SMS capability

## Troubleshooting
- Ensure credentials are correct (from the Android app)
- Check device battery optimizations aren’t killing the app
- Review server response and logs for errors

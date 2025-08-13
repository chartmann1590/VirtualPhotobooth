# Text-to-Speech (TTS)

The app supports two free TTS engines:

- Browser (Web Speech API): uses your OS/browser voices (zero server resources)
- Piper (local, lightweight neural TTS): runs in Docker with small RAM/disk usage

## Enable and Configure

1) Open Settings → TTS
2) Check “Enable TTS”
3) Choose Engine:
   - Browser: pick a system voice (install more in OS settings)
   - Piper: pick a model (downloaded to `piper/models` during deploy)
4) Set “Prompt” text (spoken before the countdown). Use the “Preview Voice” button to test

## Piper Notes
- Deploy script auto-downloads common models for English, German, Spanish, Italian, Chinese, Japanese, Korean, and Russian (male/female when available)
- Place additional `.onnx` models into `piper/models/` (mounted into containers)
- You can list voices in Settings and preview instantly

## Browser Notes
- Install OS voices for more natural speech:
  - macOS: System Settings → Accessibility → Spoken Content → Manage Voices (Enhanced/Siri voices)
  - Windows: Settings → Time & language → Speech → Manage voices
  - Linux: eSpeak NG voices (quality varies)

## Troubleshooting
- If no voices show for Browser, wait 1–2 seconds (some browsers load voices asynchronously)
- If Piper preview fails, ensure models exist in `piper/models` and the service is up (docker compose ps)

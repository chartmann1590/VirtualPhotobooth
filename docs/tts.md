# Text-to-Speech (TTS)

The app supports multiple free TTS engines:

- **Browser (Web Speech API)**: Uses your OS/browser voices (zero server resources)
- **Remote TTS Services**: High-quality voices from free online services

## Enable and Configure

1) Open Settings → TTS
2) Check "Enable TTS"
3) Choose Engine:
   - **Browser**: Pick a system voice (install more in OS settings)
   - **Remote TTS Services**: Choose from free online TTS providers
4) If using Remote TTS, select a service and voice
5) Set "Prompt" text (spoken before the countdown)
6) Use the "Preview Voice" button to test

## Available TTS Services

### Google Translate TTS
- **Languages**: 10+ languages including English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese
- **Quality**: High-quality, natural-sounding voices
- **Limits**: 200 characters per request
- **Cost**: Completely free
- **Best for**: Multi-language support, general use

### Microsoft Edge TTS
- **Languages**: 20+ languages with neural voices
- **Quality**: Natural-sounding neural voices with male/female options
- **Limits**: 500 characters per request
- **Cost**: Completely free
- **Best for**: High-quality English and European languages

### ElevenLabs (Free Tier)
- **Languages**: English only
- **Quality**: Premium AI voices (7 different voices)
- **Limits**: 2500 characters per request, 10,000 characters/month free
- **Cost**: Free tier available (requires API key)
- **Best for**: Premium voice quality, English content

### Browser TTS
- **Languages**: Depends on your OS/browser
- **Quality**: Varies by system
- **Limits**: None
- **Cost**: Free
- **Best for**: Offline use, system integration

## Setup Instructions

### Google Translate TTS
No setup required - works immediately.

### Microsoft Edge TTS
No setup required - works immediately.

### ElevenLabs
1. Visit [elevenlabs.io](https://elevenlabs.io)
2. Create a free account
3. Get your API key from the profile section
4. Enter the API key in Settings → TTS → ElevenLabs API Key

### Browser TTS
Install additional OS voices for more natural speech:
- **macOS**: System Settings → Accessibility → Spoken Content → System Voice → Manage Voices (Enhanced/Siri voices)
- **Windows**: Settings → Time & language → Speech → Manage voices → Add voices
- **Linux**: Install eSpeak NG voices (e.g., `sudo apt install espeak-ng`) and ensure your browser exposes them

## Voice Selection

- **Google**: Select language code (e.g., 'en' for English, 'es' for Spanish)
- **Microsoft**: Select specific voice (e.g., 'en-US-JennyNeural' for US English female)
- **ElevenLabs**: Select voice ID (e.g., 'Rachel', 'Josh', 'Bella')
- **Browser**: Select system voice name

## Troubleshooting

- **No voices show for Browser**: Wait 1-2 seconds (some browsers load voices asynchronously)
- **Remote TTS fails**: Check internet connection and service availability
- **ElevenLabs errors**: Verify API key is correct and has remaining quota
- **Voice quality issues**: Try different services - each has different voice characteristics
- **Character limits**: Break long text into shorter segments

## Service Comparison

| Service | Quality | Languages | Setup | Reliability |
|---------|---------|-----------|-------|-------------|
| Google | High | 10+ | None | Excellent |
| Microsoft | Very High | 20+ | None | Excellent |
| ElevenLabs | Premium | English | API Key | Good |
| Browser | Variable | System | OS Setup | Excellent |

## Best Practices

1. **For multi-language**: Use Google Translate TTS
2. **For English quality**: Use Microsoft Edge TTS
3. **For premium voices**: Use ElevenLabs (requires setup)
4. **For offline use**: Use Browser TTS
5. **For reliability**: Have multiple services configured as fallbacks

## API Limits and Costs

- **Google**: No known limits, completely free
- **Microsoft**: No known limits, completely free  
- **ElevenLabs**: 10,000 characters/month free, then $5/month for 30,000 characters
- **Browser**: No limits, completely free

All services are suitable for production use and photobooth applications.

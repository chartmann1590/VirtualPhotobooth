# Ollama AI Integration

The Virtual Photobooth now includes AI-powered prompt generation using Ollama! This feature automatically creates funny, engaging, and unique prompts for your photobooth sessions.

## What It Does

- **AI-Generated Prompts**: Creates unique, funny prompts for each photo session
- **Dynamic Content**: Every prompt is different, keeping the experience fresh
- **Contextual**: Prompts are tailored for photobooth use
- **TTS Integration**: Generated prompts are automatically used with your TTS system

## Features

### 1. **Automatic Prompt Generation**
- Generates a new prompt when the photobooth page loads
- Creates prompts that are 1-2 sentences maximum
- Ensures prompts are appropriate for all ages
- Varies content to keep each session unique

### 2. **Smart Prompt Design**
- Funny and engaging instructions
- Clear pose suggestions
- Emoji integration for visual appeal
- Photobooth-specific context

### 3. **Real-time Generation**
- "Generate New Prompt" button for on-demand prompts
- Instant feedback and display
- Seamless integration with existing TTS

## Setup Instructions

### 1. **Enable Ollama AI**
- Go to Settings → Ollama AI
- Check "Enable Ollama AI"

### 2. **Configure Remote Ollama Server**
- **Ollama URL**: Enter your remote Ollama server URL
  - Example: `https://your-ollama-server.com`
  - Example: `http://192.168.1.100:11434`
  - Example: `https://ollama.example.com`

### 3. **Select Model**
Choose from available models:
- **llama3.2** (recommended) - Best balance of quality and speed
- **llama3.1** - Good quality, slightly faster
- **llama2** - Reliable, well-tested
- **mistral** - Fast, good for creative tasks
- **codellama** - Good for structured prompts

### 4. **API Key (if required)**
- Some hosted Ollama services require API keys
- Enter the key if your service needs authentication

### 5. **Test Connection**
- Click "Test Connection" to verify Ollama is accessible
- Status will show: ✓ Connected, ✗ Failed, or ✗ Error

## How It Works

### **Prompt Generation Process**
1. **System Prompt**: Sends a detailed instruction to Ollama about creating photobooth prompts
2. **Context**: Includes photobooth-specific context for relevance
3. **AI Processing**: Ollama generates a unique, creative prompt
4. **Cleaning**: Removes quotes and formatting for clean TTS
5. **Display**: Shows the prompt in the photobooth interface
6. **TTS Integration**: Automatically uses the generated prompt for voice instructions

### **Example Prompts**
- "Strike a pose that says 'I woke up like this'! 📸"
- "Show me your best superhero landing pose! 🦸‍♂️"
- "Channel your inner rockstar and give us attitude! 🎸"
- "Pretend you just won the lottery! 🎉"
- "Look like you're about to drop the hottest album of 2024! 🎵"

## Remote Ollama Server Options

### **Self-Hosted Ollama**
```bash
# Install Ollama on your server
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model
ollama pull llama3.2
```

### **Hosted Ollama Services**
- **Ollama Cloud**: Official hosted service
- **RunPod**: GPU-powered hosting
- **Vast.ai**: Cost-effective GPU instances
- **Your own server**: VPS or dedicated machine

### **Docker Deployment**
```bash
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Configuration Examples

### **Basic Configuration**
```json
{
  "ollama": {
    "enabled": true,
    "url": "http://192.168.1.100:11434",
    "model": "llama3.2",
    "api_key": ""
  }
}
```

### **Hosted Service Configuration**
```json
{
  "ollama": {
    "enabled": true,
    "url": "https://ollama.yourdomain.com",
    "model": "llama3.2",
    "api_key": "your-api-key-here"
  }
}
```

## Troubleshooting

### **Connection Issues**
- **Check URL**: Ensure the Ollama URL is correct and accessible
- **Network**: Verify network connectivity to your Ollama server
- **Port**: Confirm port 11434 is open (default Ollama port)
- **Firewall**: Check firewall settings on both client and server

### **Model Issues**
- **Model Available**: Ensure the selected model is pulled on your Ollama server
- **Model Size**: Some models require significant RAM/VRAM
- **Model Name**: Verify the exact model name matches what's available

### **API Key Issues**
- **Required**: Some services require API keys for authentication
- **Format**: Ensure the API key is entered correctly
- **Permissions**: Verify the API key has necessary permissions

### **Performance Issues**
- **Server Specs**: Ensure your Ollama server has adequate resources
- **Model Size**: Smaller models are faster but may be less creative
- **Network Latency**: Consider server location for better response times

## Best Practices

### **Model Selection**
- **Production**: Use llama3.2 for best quality
- **Development**: Use smaller models for faster testing
- **Balance**: Consider speed vs. quality for your use case

### **Server Configuration**
- **Resources**: Ensure adequate RAM and VRAM for your chosen model
- **Network**: Use HTTPS for production deployments
- **Monitoring**: Monitor server performance and resource usage

### **Prompt Quality**
- **Temperature**: Higher values (0.8-0.9) create more creative prompts
- **Context**: Provide clear context for better relevance
- **Length**: Keep prompts under 100 characters for TTS clarity

## Security Considerations

### **Network Security**
- **HTTPS**: Use encrypted connections for production
- **Firewall**: Restrict access to necessary IPs only
- **Authentication**: Use API keys when available

### **Content Safety**
- **Filtering**: Ollama includes content filtering
- **Monitoring**: Review generated prompts for appropriateness
- **Fallbacks**: System includes fallback prompts if AI fails

## Integration with Other Features

### **TTS Integration**
- Generated prompts automatically work with all TTS services
- No additional configuration needed
- Seamless voice instruction experience

### **Photobooth Workflow**
1. Page loads → AI generates prompt
2. User sees prompt → Can generate new one if desired
3. Photo session starts → TTS speaks the AI-generated prompt
4. Countdown begins → Normal photobooth flow continues

### **Settings Integration**
- Ollama configuration saved with other app settings
- Persistent across app restarts
- Easy to modify and test

## Future Enhancements

### **Planned Features**
- **Custom Prompt Styles**: Different personality types
- **Language Support**: Multi-language prompt generation
- **Context Awareness**: Prompts based on time, events, etc.
- **User Preferences**: Save favorite prompt styles

### **API Extensions**
- **Webhook Support**: External prompt generation services
- **Custom Models**: Support for fine-tuned models
- **Batch Generation**: Generate multiple prompts at once

## Support

### **Getting Help**
- Check the troubleshooting section above
- Verify your Ollama server is running and accessible
- Test with a simple curl command:
  ```bash
  curl -X POST https://your-ollama-server.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{"model":"llama3.2","messages":[{"role":"user","content":"Hello"}]}'
  ```

### **Common Issues**
- **404 Errors**: Check if the model exists on your server
- **Timeout Errors**: Server may be overloaded or slow
- **Connection Refused**: Check if Ollama is running and accessible

The Ollama AI integration brings a new level of creativity and engagement to your photobooth experience, making each session unique and fun!

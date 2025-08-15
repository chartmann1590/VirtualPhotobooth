import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def list_models(self) -> List[Dict[str, str]]:
        """List available Ollama models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            models = []
            if 'models' in data:
                for model in data['models']:
                    models.append({
                        'name': model.get('name', ''),
                        'size': model.get('size', 0),
                        'modified_at': model.get('modified_at', ''),
                        'digest': model.get('digest', '')
                    })
            
            return models
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {str(e)}")
            return []
    
    def generate_prompt(self, model: str, context: str = "") -> str:
        """Generate a funny and informative photobooth prompt using Ollama"""
        
        # If no model is specified, try to get the first available model
        if not model:
            models = self.list_models()
            if models:
                model = models[0]['name']
            else:
                logger.error("No models available on Ollama server")
                return self._get_fallback_prompt()
        
        system_prompt = """You are a fun and engaging AI assistant for a photobooth. Your job is to generate short, funny, and informative prompts that will be spoken to people before they take a photo.

The prompt should:
- Be 1-2 sentences maximum (under 100 characters)
- Be funny and engaging
- Give clear instructions about what to do
- Be appropriate for all ages
- Vary each time to keep it interesting

Examples of good prompts:
- "Strike a pose that says 'I woke up like this'! 📸"
- "Show me your best superhero landing pose! 🦸‍♂️"
- "Channel your inner rockstar and give us attitude! 🎸"
- "Pretend you just won the lottery! 🎉"
- "Look like you're about to drop the hottest album of 2024! 🎵"

Generate a new, creative prompt that's different from the examples above."""

        user_prompt = f"Generate a photobooth prompt. {context}".strip()
        
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if 'message' in data and 'content' in data['message']:
                prompt = data['message']['content'].strip()
                # Clean up the prompt - remove quotes, extra formatting
                prompt = prompt.replace('"', '').replace('"', '').replace('"', '')
                prompt = prompt.replace("'", '').replace("'", '')
                
                # Ensure it's not too long
                if len(prompt) > 100:
                    prompt = prompt[:97] + "..."
                
                logger.info(f"Generated Ollama prompt: {prompt}")
                return prompt
            else:
                logger.error("Unexpected Ollama response format")
                return self._get_fallback_prompt()
                
        except Exception as e:
            logger.error(f"Failed to generate Ollama prompt: {str(e)}")
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Get a fallback prompt when AI generation fails"""
        fallback_prompts = [
            "Strike a pose that says 'I woke up like this'! 📸",
            "Show me your best superhero landing pose! 🦸‍♂️",
            "Channel your inner rockstar and give us attitude! 🎸",
            "Pretend you just won the lottery! 🎉",
            "Look like you're about to drop the hottest album of 2024! 🎵",
            "Give us your best 'I just had the best idea ever' face! 💡",
            "Pose like you're about to save the world! 🌍",
            "Show us your 'I'm too cool for school' look! 😎"
        ]
        import random
        return random.choice(fallback_prompts)
    
    def test_connection(self) -> bool:
        """Test if Ollama service is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {str(e)}")
            return False

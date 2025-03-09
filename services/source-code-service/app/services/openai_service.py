# services/source-code-service/app/services/openai_service.py
import logging
import json
import asyncio
import time
import os
from typing import Dict, Any, Optional, List
import aiohttp
from ..core.config import settings
from ..utils.token_counter import num_tokens_from_string

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        # Provider selection - can be "openai" or "ollama"
        self.provider = settings.LLM_PROVIDER if hasattr(settings, 'LLM_PROVIDER') else "openai"
        
        # OpenAI specific settings
        self.api_key = settings.OPENAI_API_KEY
        self.api_base = settings.OPENAI_API_BASE
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
        # Ollama specific settings (defaults if not defined in settings)
        self.ollama_api_base = getattr(settings, 'OLLAMA_API_BASE', "http://localhost:11434")
        self.ollama_model = getattr(settings, 'OLLAMA_MODEL', "llama2")
        
        self.cache_dir = settings.CACHE_DIR
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize cache
        self.cache_file = os.path.join(self.cache_dir, "openai_cache.json")
        self.cache = self._load_cache()
        
        logger.info(f"LLM Service initialized with provider: {self.provider}")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading OpenAI cache: {str(e)}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving OpenAI cache: {str(e)}")
    
    def _get_cache_key(self, prompt: str) -> str:
        """Get cache key for a prompt."""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    async def analyze_text(self, prompt: str) -> str:
        """
        Analyze text using the selected LLM provider.
        
        Args:
            prompt: Prompt for analysis
            
        Returns:
            str: Analysis result
        """
        # Check cache
        cache_key = self._get_cache_key(prompt)
        if cache_key in self.cache:
            logger.info(f"Using cached response for prompt: {prompt[:50]}...")
            return self.cache[cache_key]
        
        # Check token count
        token_count = num_tokens_from_string(prompt)
        if token_count > 4000:
            logger.warning(f"Prompt token count ({token_count}) exceeds limit, truncating...")
            # Truncate prompt to fit within limits
            prompt = self._truncate_prompt(prompt, 4000)
        
        # Choose provider
        if self.provider == "openai":
            result = await self._analyze_with_openai(prompt)
        elif self.provider == "ollama":
            result = await self._analyze_with_ollama(prompt)
        else:
            logger.error(f"Unsupported LLM provider: {self.provider}")
            return f"Error: Unsupported LLM provider: {self.provider}"
        
        # Save to cache if result is valid
        if result and not result.startswith("Error:"):
            self.cache[cache_key] = result
            self._save_cache()
        
        return result
    
    async def _analyze_with_openai(self, prompt: str) -> str:
        """
        Analyze text using OpenAI API.
        
        Args:
            prompt: Prompt for analysis
            
        Returns:
            str: Analysis result
        """
        try:
            logger.info(f"Sending request to OpenAI API: {prompt[:50]}...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a source code analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Make API request with retry logic
            async with aiohttp.ClientSession() as session:
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        async with session.post(
                            f"{self.api_base}/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=60
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                return data['choices'][0]['message']['content']
                            else:
                                error_data = await response.text()
                                logger.error(f"OpenAI API error ({response.status}): {error_data}")
                                if response.status == 429:  # Rate limit error
                                    # Exponential backoff
                                    wait_time = (2 ** attempt) + 1
                                    logger.info(f"Rate limited, waiting {wait_time} seconds...")
                                    await asyncio.sleep(wait_time)
                                else:
                                    break  # Don't retry other errors
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        logger.error(f"Request error: {str(e)}")
                        await asyncio.sleep(1)
                
                # If we got here, all attempts failed
                logger.error(f"All OpenAI API attempts failed")
                return "Error: Could not get a response from the OpenAI API after multiple attempts."
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
    
    async def _analyze_with_ollama(self, prompt: str) -> str:
        """
        Analyze text using Ollama API.
        
        Args:
            prompt: Prompt for analysis
            
        Returns:
            str: Analysis result
        """
        try:
            logger.info(f"Sending request to Ollama API: {prompt[:50]}...")
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                }
            }
            
            # Make API request with retry logic
            async with aiohttp.ClientSession() as session:
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        async with session.post(
                            f"{self.ollama_api_base}/api/generate",
                            json=payload,
                            timeout=120  # Longer timeout for local models
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                return data.get('response', '')
                            else:
                                error_data = await response.text()
                                logger.error(f"Ollama API error ({response.status}): {error_data}")
                                # Simple retry with delay
                                await asyncio.sleep(2)
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        logger.error(f"Request error: {str(e)}")
                        await asyncio.sleep(2)
                
                # If we got here, all attempts failed
                logger.error(f"All Ollama API attempts failed")
                return "Error: Could not get a response from the Ollama API after multiple attempts."
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
    
    def _truncate_prompt(self, prompt: str, max_tokens: int) -> str:
        """
        Truncate prompt to fit within token limit.
        
        Args:
            prompt: Prompt to truncate
            max_tokens: Maximum tokens allowed
            
        Returns:
            str: Truncated prompt
        """
        while num_tokens_from_string(prompt) > max_tokens:
            # Cut 10% of the prompt each time
            length = len(prompt)
            cut_length = int(length * 0.1)
            prompt = prompt[:length - cut_length]
        
        return prompt
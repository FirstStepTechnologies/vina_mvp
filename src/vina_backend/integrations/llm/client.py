"""
LLM client wrapper for litellm.
Provides a unified interface for multiple LLM providers (Anthropic, OpenAI, Gemini).
"""
import json
import logging
import time
from typing import Any, Dict, Optional, Literal, List
from litellm import completion

from vina_backend.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


# Model recommendations by provider
RECOMMENDED_MODELS = {
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20241213",
        "claude-3-5-sonnet-20241022",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
    ],
    "gemini": [
    "gemini-3-flash-preview", 
        "gemini-3-pro-preview",   
        "gemini-2.5-flash",       
    ],
}

# Fallback models when primary model fails (in order of preference)
FALLBACK_MODELS = {
    "gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ],
    "openai": [
        "gpt-4.1-mini",
        "gpt-4o-mini",
    ],
    "anthropic": [
        "claude-haiku-4-5-20251001",
        "claude-sonnet-5-20260203",
    ],
}


class LLMClient:
    """Wrapper around litellm for making LLM API calls across multiple providers."""
    
    def __init__(
        self,
        provider: Optional[Literal["anthropic", "openai", "gemini"]] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use (defaults to settings)
            model: Model to use (defaults to settings)
            api_key: API key (defaults to settings based on provider)
        """
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        
        # Get API key for the active provider
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = settings.get_active_api_key()
        
        # Validate model matches provider
        self._validate_model()
    
    def _get_litellm_model_name(self) -> str:
        """
        Format model name for litellm.
        litellm requires provider prefix for some providers (e.g., 'gemini/gemini-3-flash').
        
        Returns:
            Properly formatted model name for litellm
        """
        # litellm expects provider prefixes for certain providers
        if self.provider == "gemini" and not self.model.startswith("gemini/"):
            return f"gemini/{self.model}"
        elif self.provider == "openai" and not self.model.startswith("openai/"):
            # OpenAI models can work without prefix, but let's be explicit
            return self.model
        elif self.provider == "anthropic" and not self.model.startswith("anthropic/"):
            # Anthropic models work without prefix
            return self.model
        else:
            return self.model
    
    def _validate_model(self):
        """
        Warn if model doesn't match the provider.
        Helps catch config errors like using 'gpt-4' with anthropic provider.
        """
        recommended = RECOMMENDED_MODELS.get(self.provider, [])
        
        # Check if model starts with expected prefix
        if self.provider == "anthropic" and not self.model.startswith("claude"):
            logger.warning(f"Using model '{self.model}' with provider '{self.provider}'")
            logger.info(f"Recommended models: {', '.join(recommended[:2])}")
        elif self.provider == "openai" and not self.model.startswith("gpt"):
            logger.warning(f"Using model '{self.model}' with provider '{self.provider}'")
            logger.info(f"Recommended models: {', '.join(recommended[:2])}")
        elif self.provider == "gemini" and not self.model.startswith("gemini"):
            logger.warning(f"Using model '{self.model}' with provider '{self.provider}'")
            logger.info(f"Recommended models: {', '.join(recommended[:2])}")
    
    def _get_safe_temperature(self, requested_temp: Optional[float] = None) -> float:
        """
        Calculate a safe temperature based on 2026 provider guidelines.
        
        Special handling for Gemini 3 models which require temperature=1.0
        to avoid infinite loops and degraded reasoning performance.
        """
        # Check if this is a Gemini 3 model (gemini-3-* variants)
        is_gemini_3 = self.provider == "gemini" and "gemini-3" in self.model.lower()
        
        # Force temperature=1.0 for Gemini 3 models (override requested temp)
        if is_gemini_3:
            if requested_temp is not None and requested_temp < 1.0:
                logger.warning(
                    f"Overriding temperature {requested_temp} → 1.0 for {self.model}. "
                    f"Gemini 3 models require temp=1.0 to avoid infinite loops and degraded performance."
                )
            return 1.0
        
        # For non-Gemini-3 models, respect requested temperature if provided
        if requested_temp is not None:
            return requested_temp

        # Use provider-specific defaults when no temperature is requested
        if self.provider == "gemini":
            return 1.0  # Safe default for Gemini 2.5 and other Gemini models
        elif self.provider == "anthropic":
            return 0.3  # Precision focus for Claude 4.5 analytical tasks
        elif self.provider == "openai":
            # Check for reasoning models (o-series, gpt-5)
            if any(m in self.model for m in ["o1", "o3", "gpt-5"]):
                return 1.0
            return settings.llm_temperature
        
        return settings.llm_temperature

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
        max_retries: int = 2,
        retry_delay: float = 1.0,
    ) -> str:
        """
        Generate text using the LLM with automatic fallback on 503 errors.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate (defaults to settings)
            temperature: Sampling temperature 0-1 (None for intelligent default)
            system: Optional system prompt
            max_retries: Maximum number of retries for rate limit errors (default: 2)
            retry_delay: Delay between retries in seconds for rate limits (default: 1.0)
        
        Returns:
            Generated text response
        
        Raises:
            ValueError: If generation fails after all model fallbacks
        """
        max_tokens = max_tokens or settings.llm_max_tokens
        safe_temp = self._get_safe_temperature(temperature)
        
        # Build messages for litellm
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Try with primary model first, then fallback models
        models_to_try = [self.model] + FALLBACK_MODELS.get(self.provider, [])
        
        last_error = None
        for model_index, model in enumerate(models_to_try):
            # Skip if this fallback model is the same as primary
            if model_index > 0 and model == self.model:
                continue
            
            # Try this model
            for attempt in range(max_retries):
                try:
                    # Update model for this attempt
                    current_model = model
                    formatted_model = f"{self.provider}/{current_model}" if self.provider == "gemini" else current_model
                    
                    if model_index > 0 and attempt == 0:
                        logger.warning(f"Falling back to model: {formatted_model}")
                    
                    if attempt > 0:
                        logger.info(f"Retry {attempt}/{max_retries-1} for {formatted_model}")
                    else:
                        logger.info(f"Calling LLM ({formatted_model}) with {len(messages)} messages and temperature {safe_temp}")
                    
                    # Track call duration
                    start_time = time.time()
                    
                    # litellm handles provider routing internally based on model name
                    response = completion(
                        model=formatted_model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=safe_temp,
                        api_key=self.api_key,
                    )
                    
                    duration = time.time() - start_time
                    logger.info(f"LLM call to {formatted_model} took {duration:.2f}s")
                    
                    logger.debug(f"LLM response received. Length: {len(response.choices[0].message.content)} chars")
                    
                    # Success! Update the instance model if we used a fallback
                    if model != self.model:
                        logger.info(f"Successfully switched from {self.model} to {model}")
                        self.model = model
                    
                    return response.choices[0].message.content.strip()
                
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    
                    # Check error type
                    is_overloaded = any(code in error_str for code in ["503", "UNAVAILABLE", "overloaded"])
                    is_rate_limit = "429" in error_str
                    is_server_error = "500" in error_str
                    
                    # For 503/overload errors, immediately try next model (no retries)
                    if is_overloaded:
                        logger.warning(f"Model {formatted_model} is overloaded (503). Switching to next model...")
                        break  # Move to next model immediately
                    
                    # For rate limits (429), retry with backoff
                    elif is_rate_limit and attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit with {formatted_model}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    # For other errors, try next model
                    else:
                        if is_rate_limit:
                            logger.error(f"Model {formatted_model} rate limit persists after retries")
                        else:
                            logger.error(f"Error with {formatted_model}: {error_str}")
                        break  # Move to next model
        
        # All models failed
        logger.exception(f"All models failed for provider {self.provider}")
        raise ValueError(
            f"LLM generation failed with {self.provider} after trying models {models_to_try}: {str(last_error)}"
        ) from last_error
    
    def generate_json(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate JSON using the LLM and parse it.
        
        Handles common formatting issues like markdown code fences.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: Optional system prompt
        
        Returns:
            Parsed JSON as dictionary
        
        Raises:
            ValueError: If generation or parsing fails
        """
        response = self.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
        )
        
        # Clean up common formatting issues
        cleaned = self._clean_json_response(response)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse LLM response as JSON: {str(e)}\n"
                f"Provider: {self.provider}, Model: {self.model}\n"
                f"Response was: {response[:500]}..."
            ) from e
    
    @staticmethod
    def _clean_json_response(text: str) -> str:
        """
        Remove markdown code fences and other common artifacts from LLM JSON responses.
        
        Different providers have different formatting habits:
        - Anthropic: Usually clean JSON, sometimes with ```json fences
        - OpenAI: Often adds ```json fences
        - Gemini: Sometimes adds explanation before/after JSON
        
        Args:
            text: Raw response text
        
        Returns:
            Cleaned text ready for JSON parsing
        """
        text = text.strip()
        
        # Remove markdown code fences
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Some models add explanatory text before/after JSON
        # Try to extract just the JSON object
        if not text.startswith("{"):
            # Find first { and last }
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                text = text[start:end]
        
        return text.strip()
    
    def get_info(self) -> Dict[str, str]:
        """
        Get information about the current LLM configuration.
        
        Returns:
            Dictionary with provider, model, and API key status
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_set": bool(self.api_key),
            "api_key_preview": f"{self.api_key[:8]}..." if self.api_key else "NOT SET",
        }


# Global client instance (lazy initialization)
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create the global LLM client instance.
    
    Returns:
        LLM client instance configured from settings
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
        
        # Log which provider/model we're using
        info = _llm_client.get_info()
        logger.info(f"LLM Client initialized: {info['provider']}/{info['model']}")
    
    return _llm_client


def reset_llm_client():
    """
    Reset the global LLM client.
    Useful for testing or switching providers at runtime.
    """
    global _llm_client
    _llm_client = None
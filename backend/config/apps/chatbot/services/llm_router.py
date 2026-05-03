"""Unified LLM interface with Gemini primary and OpenAI fallback.
Uses google-genai (new SDK) for Gemini, OpenAI SDK for fallback.
Implements dynamic model discovery and caching for Gemini.
"""
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global cache for discovered Gemini model name
_cached_gemini_model: Optional[str] = None


def _discover_gemini_model(api_key: str) -> Optional[str]:
    """Discover the best available Gemini model at runtime.
    
    Queries the Gemini API to list available models and selects
    the best model containing 'flash' in its name.
    
    Args:
        api_key: The Gemini API key
        
    Returns:
        str: The model name (e.g., 'models/gemini-1.5-flash')
        None: If no suitable model is found
    """
    global _cached_gemini_model
    
    # Return cached model if available
    if _cached_gemini_model:
        return _cached_gemini_model
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        models = client.models.list()
        flash_models = []
        
        for model in models:
            model_name = model.name
            # Look for models with 'flash' in the name (case-insensitive)
            if 'flash' in model_name.lower():
                flash_models.append(model_name)
        
        if not flash_models:
            logger.warning("No Gemini flash models found")
            return None
        
        # Prefer newer versions - sort to get the best model
        # Models are typically named like 'models/gemini-1.5-flash'
        flash_models.sort(reverse=True)
        best_model = flash_models[0]
        
        _cached_gemini_model = best_model
        logger.info(f"Discovered Gemini model: {best_model}")
        return best_model
        
    except Exception as e:
        logger.error(f"Failed to discover Gemini models: {e}")
        return None


def call_llm(prompt: str, mode: str = "general") -> str:
    """
    Call LLM with Gemini as primary, OpenAI as fallback.

    Args:
        prompt: The prompt to send to the LLM
        mode: "intent", "explanation", or "general"

    Returns:
        str: The LLM response text

    Rules:
        - Gemini (google-genai SDK) is tried first (retry once on failure)
        - OpenAI is used as fallback
        - Never exposes API errors to caller
        - Dynamic model discovery with caching
    """
    print(f"\n[LLM ROUTER] call_llm called (mode={mode})")
    print(f"[LLM ROUTER] PROMPT SENT TO LLM:")
    print("-"*60)
    print(prompt)
    print("-"*60)
    
    # Try Gemini first
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        gemini_model = _discover_gemini_model(gemini_key)
        
        if gemini_model:
            for attempt in range(2):
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_key)
                    
                    print(f"[LLM ROUTER] Trying Gemini (model={gemini_model}, attempt={attempt+1})...")
                    response = client.models.generate_content(
                        model=gemini_model,
                        contents=prompt
                    )
                    text = response.text.strip()
                    print(f"[LLM ROUTER] GEMINI RESPONSE:")
                    print("-"*60)
                    print(text)
                    print("-"*60)
                    logger.info(f"LLM call successful via gemini (mode={mode}, model={gemini_model})")
                    return _sanitize_response(text, mode)
                    
                except Exception as e:
                    print(f"[LLM ROUTER] Gemini attempt {attempt + 1} failed: {e}")
                    logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
                    if attempt == 0:
                        continue
    
    print(f"[LLM ROUTER] Gemini failed, falling back to OpenAI...")
    logger.warning("Gemini unavailable or failed, trying OpenAI fallback")
    
    # Fallback to OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            temperature = 0 if mode == "intent" else 0.7
            print(f"[LLM ROUTER] Trying OpenAI (model=gpt-4o-mini, temperature={temperature})...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()
            print(f"[LLM ROUTER] OPENAI RESPONSE:")
            print("-"*60)
            print(text)
            print("-"*60)
            logger.info(f"LLM call successful via openai (mode={mode})")
            return _sanitize_response(text, mode)
        except Exception as e:
            print(f"[LLM ROUTER] OpenAI fallback failed: {e}")
            logger.error(f"OpenAI fallback failed: {e}")
            return _safe_error_response(mode)
    
    logger.error("No LLM API keys available")
    return _safe_error_response(mode)


def _sanitize_response(text: str, mode: str) -> str:
    """Sanitize and validate LLM response."""
    if mode == "intent":
        # Strip markdown code blocks if present
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3].strip()
        elif text.startswith("```") and text.endswith("```"):
            text = text[3:-3].strip()
        # Validate it's parseable JSON
        try:
            json.loads(text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
    return text


def _safe_error_response(mode: str) -> str:
    """Return safe error response based on mode."""
    if mode == "intent":
        return '{"intent": "UNKNOWN", "fields": {}, "confidence": 0.0}'
    return "I'm having trouble processing your request right now. Please try again later."

import json
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class OllamaResponse:
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "phi3:latest"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> OllamaResponse:
        import requests
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            content = response.json().get("response", "")
            return OllamaResponse(success=True, content=content)
        except requests.exceptions.ConnectionError:
            return OllamaResponse(success=False, error="Ollama not running. Start with 'ollama serve'")
        except requests.exceptions.RequestException as e:
            return OllamaResponse(success=False, error=str(e))
        except json.JSONDecodeError as e:
            return OllamaResponse(success=False, error=str(e))
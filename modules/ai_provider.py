"""Local AI Provider using Ollama for SkillBridge AI.

Supports local open-weight models (e.g. llama3.2, mistral, phi3) with zero cloud
dependency, strict timeouts, error handling, and transparent provenance tracking.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import requests

from config import DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS


class OllamaProvider:
    """Interface to local Ollama runtime."""

    def __init__(
        self,
        host: str = DEFAULT_OLLAMA_HOST,
        model: str = DEFAULT_OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT_SECONDS,
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def check_availability(self) -> Tuple[bool, str, List[str]]:
        """Checks if local Ollama server is running and queries available models.

        Returns:
            (is_available, status_message, list_of_model_names)
        """
        url = f"{self.host}/api/tags"
        try:
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                models_raw = data.get("models", [])
                model_names = [m.get("name", "") for m in models_raw if m.get("name")]
                return (
                    True,
                    f"Ollama is online at {self.host}. Detected {len(model_names)} installed model(s).",
                    model_names,
                )
            else:
                return (
                    False,
                    f"Ollama server responded with HTTP {resp.status_code}.",
                    [],
                )
        except requests.exceptions.ConnectionError:
            return (
                False,
                f"Cannot connect to Ollama at {self.host}. Ensure Ollama is installed and running (`ollama serve`).",
                [],
            )
        except requests.exceptions.Timeout:
            return (
                False,
                f"Connection to Ollama at {self.host} timed out after {self.timeout}s.",
                [],
            )
        except Exception as e:
            return (
                False,
                f"Ollama connection error: {str(e)}",
                [],
            )

    def generate_completion(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """Sends prompt to local Ollama API.

        Returns:
            (success: bool, response_or_error: str, provider_source: str)
        """
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                result = resp.json()
                response_text = result.get("response", "").strip()
                if response_text:
                    return True, response_text, f"Local Ollama AI ({self.model})"
                else:
                    return False, "Empty response from Ollama model.", "Fallback Engine"
            else:
                return (
                    False,
                    f"Ollama returned HTTP error {resp.status_code}: {resp.text}",
                    "Fallback Engine",
                )
        except requests.exceptions.ConnectionError:
            return (
                False,
                "Ollama service is unreachable (Connection Refused). Using deterministic fallback.",
                "Fallback Engine",
            )
        except requests.exceptions.Timeout:
            return (
                False,
                f"Ollama request timed out after {self.timeout} seconds. Using deterministic fallback.",
                "Fallback Engine",
            )
        except Exception as e:
            return (
                False,
                f"Local AI request failed: {str(e)}. Using deterministic fallback.",
                "Fallback Engine",
            )

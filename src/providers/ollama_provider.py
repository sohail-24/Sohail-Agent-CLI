"""Ollama provider for local AI model integration."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from .base_provider import BaseProvider, GenerationRequest, GenerationResult, ProviderConfig


class OllamaProvider(BaseProvider):
    """
    Provider for Ollama local AI models.
    
    This provider connects to a local Ollama instance
    for text generation using locally hosted models.
    """
    
    def __init__(self, config: ProviderConfig | None = None) -> None:
        """
        Initialize the Ollama provider.
        
        Args:
            config: Provider configuration with Ollama-specific settings
        """
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return "ollama"
    
    @property
    def is_local(self) -> bool:
        """Check if this is a local provider."""
        return True
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        return self._client
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate text using Ollama.
        
        Args:
            request: The generation request
        
        Returns:
            The generation result
        """
        client = self._get_client()
        
        model = request.model or self.config.default_model
        
        payload: dict[str, Any] = {
            "model": model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                **request.options,
            },
        }
        
        if request.system:
            payload["system"] = request.system
        
        if request.context:
            payload["context"] = request.context
        
        try:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            return GenerationResult(
                text=data.get("response", ""),
                model=model,
                done=data.get("done", True),
                context=data.get("context"),
                total_duration_ms=data.get("total_duration", 0) / 1_000_000,
                load_duration_ms=data.get("load_duration", 0) / 1_000_000,
                prompt_eval_count=data.get("prompt_eval_count"),
                eval_count=data.get("eval_count"),
            )
        
        except httpx.HTTPStatusError as e:
            return GenerationResult.error_result(
                f"HTTP error {e.response.status_code}: {e.response.text}"
            )
        except httpx.ConnectError:
            return GenerationResult.error_result(
                f"Cannot connect to Ollama at {self.config.base_url}. "
                "Is Ollama running?"
            )
        except Exception as e:
            return GenerationResult.error_result(str(e))
    
    async def generate_stream(
        self, 
        request: GenerationRequest,
    ) -> AsyncIterator[GenerationResult]:
        """
        Generate text with streaming from Ollama.
        
        Args:
            request: The generation request
        
        Yields:
            Generation results as they become available
        """
        client = self._get_client()
        
        model = request.model or self.config.default_model
        
        payload: dict[str, Any] = {
            "model": model,
            "prompt": request.prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature,
                **request.options,
            },
        }
        
        if request.system:
            payload["system"] = request.system
        
        if request.context:
            payload["context"] = request.context
        
        try:
            async with client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        yield GenerationResult(
                            text=data.get("response", ""),
                            model=model,
                            done=data.get("done", False),
                            context=data.get("context"),
                            total_duration_ms=data.get("total_duration", 0) / 1_000_000,
                        )
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            yield GenerationResult.error_result(str(e))
    
    async def list_models(self) -> list[str]:
        """
        List available Ollama models.
        
        Returns:
            List of model names
        """
        client = self._get_client()
        
        try:
            response = await client.get("/api/tags")
            response.raise_for_status()
            
            data = response.json()
            models = data.get("models", [])
            
            return [m.get("name", "") for m in models if m.get("name")]
        
        except Exception:
            return []
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is running.
        
        Returns:
            True if Ollama is available
        """
        client = self._get_client()
        
        try:
            response = await client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    async def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama.
        
        Args:
            model: The model name to pull
        
        Returns:
            True if successful
        """
        client = self._get_client()
        
        try:
            response = await client.post(
                "/api/pull",
                json={"name": model, "stream": False},
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

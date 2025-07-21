"""
Ollama client implementation for local LLM support.

This module provides integration with Ollama for running multi-modal
language models locally.
"""

import os
import json
from typing import Dict, List, Optional, Any
import httpx
from loguru import logger

from models.llm_interface import LLMInterface, LLMResponse, ImageInput


class OllamaClient(LLMInterface):
    """
    Client for interacting with Ollama-hosted models.
    
    Ollama enables running large language models locally, including
    multi-modal models like LLaVA for image analysis.
    """
    
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            model_name: Model to use (default: llava)
        """
        super().__init__(model_name or "llava")
        self.base_url = base_url or "http://localhost:11434"
        self.timeout = 300  # 5 minutes for large models
        
        # Ensure base URL doesn't end with slash
        self.base_url = self.base_url.rstrip("/")
        
        logger.info(f"Initialized Ollama client with base URL: {self.base_url}")
    
    async def generate(
        self,
        prompt: str,
        images: Optional[List[ImageInput]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: Text prompt for the model
            images: Optional list of images for multi-modal models
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional Ollama-specific parameters
            
        Returns:
            LLMResponse: Generated response
            
        Raises:
            ValueError: If request fails
        """
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        # Add max tokens if specified
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        # Add images if provided
        if images:
            # Validate images
            for img in images:
                self.validate_image_input(img)
            
            # Ollama expects images as base64 strings in an array
            payload["images"] = [img.base64 for img in images]
        
        # Make request
        endpoint = f"{self.base_url}/api/generate"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending request to Ollama: {endpoint}")
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    error_msg = f"Ollama request failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Parse response
                data = response.json()
                
                # Extract token usage if available
                usage = None
                if "eval_count" in data:
                    usage = {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    }
                
                logger.info(f"Ollama generation completed in {data.get('total_duration', 0) / 1e9:.2f}s")
                
                return LLMResponse(
                    content=data.get("response", ""),
                    usage=usage,
                    model=self.model_name,
                    provider="ollama",
                    raw_response=data
                )
                
        except httpx.TimeoutException:
            error_msg = f"Ollama request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Failed to connect to Ollama at {self.base_url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            logger.exception("Unexpected error in Ollama generation")
            raise ValueError(f"Ollama generation failed: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            bool: True if Ollama is running and model is available
        """
        try:
            # Check if Ollama is running
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                
                if response.status_code != 200:
                    logger.warning(f"Ollama not responding properly: {response.status_code}")
                    return False
                
                # Check if our model is available
                data = response.json()
                available_models = [
                    model["name"].split(":")[0]  # Remove tag
                    for model in data.get("models", [])
                ]
                
                if self.model_name not in available_models:
                    logger.warning(f"Model {self.model_name} not found in Ollama. Available: {available_models}")
                    return False
                
                logger.debug(f"Ollama is available with model {self.model_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to check Ollama availability: {str(e)}")
            return False
    
    def supports_images(self) -> bool:
        """
        Check if this model supports image inputs.
        
        Returns:
            bool: True if model supports images
        """
        # Known multi-modal models in Ollama
        multimodal_models = [
            "llava",
            "bakllava",
            "llava-v1.5",
            "llava-v1.6",
            "cogvlm"
        ]
        
        # Check if current model is multi-modal
        model_base = self.model_name.split(":")[0].lower()
        return model_base in multimodal_models
    
    async def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Pull a model from Ollama registry if not available locally.
        
        Args:
            model_name: Model to pull (default: configured model)
            
        Returns:
            bool: True if successful
        """
        model_to_pull = model_name or self.model_name
        
        try:
            logger.info(f"Pulling model {model_to_pull} from Ollama registry...")
            
            async with httpx.AsyncClient(timeout=3600) as client:  # 1 hour timeout for large models
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_to_pull},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully pulled model {model_to_pull}")
                    return True
                else:
                    logger.error(f"Failed to pull model: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models in Ollama.
        
        Returns:
            list: Available models with metadata
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("models", [])
                else:
                    logger.error(f"Failed to list models: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def prepare_prompt_with_images(
        self,
        prompt: str,
        images: List[ImageInput]
    ) -> Dict[str, Any]:
        """
        Prepare Ollama-specific prompt format with images.
        
        Args:
            prompt: Text prompt
            images: List of images
            
        Returns:
            dict: Formatted prompt data
        """
        # For Ollama, we can include image references in the prompt
        # Some models work better with explicit image references
        
        if len(images) == 1:
            enhanced_prompt = f"[Image provided]\n\n{prompt}"
        else:
            enhanced_prompt = f"[{len(images)} images provided]\n\n{prompt}"
        
        return {
            "prompt": enhanced_prompt,
            "images": [img.base64 for img in images]
        }
"""
Cloud-based LLM client implementations.

This module provides integrations with OpenAI and Anthropic APIs for
multi-modal language model capabilities.
"""

import os
from typing import Dict, List, Optional, Any
import httpx
import base64
from loguru import logger

from models.llm_interface import LLMInterface, LLMResponse, ImageInput


class OpenAIClient(LLMInterface):
    """
    Client for interacting with OpenAI's GPT models.
    
    Supports GPT-4 Vision for multi-modal analysis of architecture diagrams.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model_name: Model to use (default: gpt-4-vision-preview)
        """
        super().__init__(model_name or "gpt-4-vision-preview")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.timeout = 120
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        logger.info(f"Initialized OpenAI client with model: {self.model_name}")
    
    async def generate(
        self,
        prompt: str,
        images: Optional[List[ImageInput]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using OpenAI's API.
        
        Args:
            prompt: Text prompt
            images: Optional images for vision models
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional OpenAI parameters
            
        Returns:
            LLMResponse: Generated response
        """
        # Build messages array
        messages = []
        
        # Create user message content
        content = [{"type": "text", "text": prompt}]
        
        # Add images if provided
        if images:
            for img in images:
                self.validate_image_input(img)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{img.mime_type};base64,{img.base64}"
                    }
                })
        
        messages.append({"role": "user", "content": content})
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096
        }
        
        # Add any additional parameters
        payload.update(kwargs)
        
        # Make request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending request to OpenAI API")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = f"OpenAI API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Parse response
                data = response.json()
                
                # Extract usage information
                usage = None
                if "usage" in data:
                    usage = {
                        "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                        "completion_tokens": data["usage"].get("completion_tokens", 0),
                        "total_tokens": data["usage"].get("total_tokens", 0)
                    }
                
                # Get the response content
                content = data["choices"][0]["message"]["content"]
                
                logger.info(f"OpenAI generation completed")
                
                return LLMResponse(
                    content=content,
                    usage=usage,
                    model=data.get("model", self.model_name),
                    provider="openai",
                    raw_response=data
                )
                
        except httpx.TimeoutException:
            error_msg = f"OpenAI request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            logger.exception("Unexpected error in OpenAI generation")
            raise ValueError(f"OpenAI generation failed: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if OpenAI API is available.
        
        Returns:
            bool: True if API is accessible
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Failed to check OpenAI availability: {str(e)}")
            return False
    
    def supports_images(self) -> bool:
        """
        Check if model supports images.
        
        Returns:
            bool: True for vision models
        """
        vision_models = ["gpt-4-vision-preview", "gpt-4-turbo", "gpt-4o"]
        return any(vm in self.model_name for vm in vision_models)


class AnthropicClient(LLMInterface):
    """
    Client for interacting with Anthropic's Claude models.
    
    Supports Claude 3 models with vision capabilities for diagram analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key
            model_name: Model to use (default: claude-3-opus-20240229)
        """
        super().__init__(model_name or "claude-3-opus-20240229")
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        self.timeout = 120
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        logger.info(f"Initialized Anthropic client with model: {self.model_name}")
    
    async def generate(
        self,
        prompt: str,
        images: Optional[List[ImageInput]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using Anthropic's API.
        
        Args:
            prompt: Text prompt
            images: Optional images for vision models
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse: Generated response
        """
        # Build messages array
        messages = []
        
        # Create message content
        content = []
        
        # Add images first if provided
        if images:
            for img in images:
                self.validate_image_input(img)
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": img.mime_type,
                        "data": img.base64
                    }
                })
        
        # Add text prompt
        content.append({
            "type": "text",
            "text": prompt
        })
        
        messages.append({
            "role": "user",
            "content": content
        })
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096
        }
        
        # Add any additional parameters
        if "system" in kwargs:
            payload["system"] = kwargs["system"]
        
        # Make request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending request to Anthropic API")
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = f"Anthropic API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Parse response
                data = response.json()
                
                # Extract usage information
                usage = None
                if "usage" in data:
                    usage = {
                        "prompt_tokens": data["usage"].get("input_tokens", 0),
                        "completion_tokens": data["usage"].get("output_tokens", 0),
                        "total_tokens": (
                            data["usage"].get("input_tokens", 0) + 
                            data["usage"].get("output_tokens", 0)
                        )
                    }
                
                # Get the response content
                content_blocks = data.get("content", [])
                content = ""
                for block in content_blocks:
                    if block.get("type") == "text":
                        content += block.get("text", "")
                
                logger.info(f"Anthropic generation completed")
                
                return LLMResponse(
                    content=content,
                    usage=usage,
                    model=data.get("model", self.model_name),
                    provider="anthropic",
                    raw_response=data
                )
                
        except httpx.TimeoutException:
            error_msg = f"Anthropic request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            logger.exception("Unexpected error in Anthropic generation")
            raise ValueError(f"Anthropic generation failed: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if Anthropic API is available.
        
        Returns:
            bool: True if API is accessible
        """
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Simple request to check authentication
            async with httpx.AsyncClient(timeout=10) as client:
                # Use a minimal request to test connectivity
                response = await client.post(
                    f"{self.base_url}/messages",
                    json={
                        "model": "claude-3-haiku-20240307",  # Cheapest model
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1
                    },
                    headers=headers
                )
                
                # 200 means it worked, 401 means bad auth, both mean API is up
                return response.status_code in [200, 401]
                
        except Exception as e:
            logger.error(f"Failed to check Anthropic availability: {str(e)}")
            return False
    
    def supports_images(self) -> bool:
        """
        Check if model supports images.
        
        Returns:
            bool: True for Claude 3 models
        """
        # All Claude 3 models support vision
        return "claude-3" in self.model_name
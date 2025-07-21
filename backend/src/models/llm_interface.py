"""
Abstract interface for LLM providers.

This module defines the contract that all LLM implementations must follow,
enabling easy switching between different providers (Ollama, OpenAI, Anthropic).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from loguru import logger


@dataclass
class LLMResponse:
    """
    Standardized response from any LLM provider.
    
    Attributes:
        content: The main response content
        usage: Token/resource usage information
        model: Model name used for generation
        provider: Provider name (ollama, openai, anthropic)
        raw_response: Original response from the provider
    """
    content: str
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    raw_response: Optional[Any] = None


@dataclass
class ImageInput:
    """
    Standardized image input for multi-modal LLMs.
    
    Attributes:
        base64: Base64 encoded image data
        mime_type: MIME type of the image
        metadata: Additional image metadata
    """
    base64: str
    mime_type: str = "image/png"
    metadata: Optional[Dict] = None


class LLMInterface(ABC):
    """
    Abstract base class for LLM providers.
    
    This interface ensures consistent behavior across different LLM implementations,
    making it easy to switch providers or add new ones.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the LLM interface.
        
        Args:
            model_name: Specific model to use (provider-dependent)
        """
        self.model_name = model_name
        self.provider_name = self.__class__.__name__.replace("Client", "").lower()
        
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        images: Optional[List[ImageInput]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: Text prompt for the LLM
            images: Optional list of images for multi-modal models
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse: Standardized response object
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the LLM service is available and properly configured.
        
        Returns:
            bool: True if service is available
        """
        pass
    
    @abstractmethod
    def supports_images(self) -> bool:
        """
        Check if this provider supports image inputs.
        
        Returns:
            bool: True if multi-modal capabilities are supported
        """
        pass
    
    def validate_image_input(self, image: ImageInput) -> bool:
        """
        Validate that an image input meets provider requirements.
        
        Args:
            image: Image input to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If image input is invalid
        """
        if not image.base64:
            raise ValueError("Image base64 data is required")
            
        if not image.mime_type:
            raise ValueError("Image MIME type is required")
            
        # Check base64 format
        try:
            import base64
            base64.b64decode(image.base64)
        except Exception:
            raise ValueError("Invalid base64 image data")
            
        return True
    
    def prepare_prompt_with_images(
        self,
        prompt: str,
        images: List[ImageInput]
    ) -> Dict[str, Any]:
        """
        Prepare a prompt with embedded images for the provider.
        
        This method can be overridden by providers that need special formatting.
        
        Args:
            prompt: Text prompt
            images: List of images to include
            
        Returns:
            dict: Provider-specific prompt structure
        """
        # Default implementation - providers can override
        return {
            "text": prompt,
            "images": [
                {
                    "base64": img.base64,
                    "mime_type": img.mime_type
                }
                for img in images
            ]
        }
    
    async def analyze_architecture_diagram(
        self,
        image_path: Path,
        output_format: str = "terraform"
    ) -> Dict[str, Any]:
        """
        High-level method to analyze an architecture diagram.
        
        Args:
            image_path: Path to the diagram image
            output_format: Desired output format (terraform/cloudformation)
            
        Returns:
            dict: Analysis results including generated code
        """
        from services.image_processor import ImageProcessor
        from services.prompt_manager import PromptManager
        
        # Prepare image
        processor = ImageProcessor()
        image_data = processor.prepare_for_llm(image_path)
        
        # Create image input
        image_input = ImageInput(
            base64=image_data["base64"],
            mime_type=image_data["mime_type"],
            metadata=image_data["metadata"]
        )
        
        # Get appropriate prompt
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_architecture_prompt(output_format)
        
        # Generate response
        logger.info(f"Analyzing architecture diagram with {self.provider_name}")
        response = await self.generate(
            prompt=prompt,
            images=[image_input],
            temperature=0.1,  # Low temperature for consistent output
            max_tokens=4000  # Sufficient for most IaC code
        )
        
        # Parse the response to extract code and metadata
        return self._parse_architecture_response(response.content, output_format)
    
    def _parse_architecture_response(
        self,
        response: str,
        output_format: str
    ) -> Dict[str, Any]:
        """
        Parse LLM response to extract code and metadata.
        
        Args:
            response: Raw LLM response
            output_format: Expected code format
            
        Returns:
            dict: Parsed response with code and metadata
        """
        import re
        
        # Extract code blocks
        code_pattern = r"```(?:hcl|terraform|yaml|json)?\n(.*?)```"
        code_matches = re.findall(code_pattern, response, re.DOTALL)
        
        if not code_matches:
            # Try to find code without language specifier
            code_pattern = r"```\n(.*?)```"
            code_matches = re.findall(code_pattern, response, re.DOTALL)
        
        code = code_matches[0].strip() if code_matches else ""
        
        # Extract resource mentions
        resource_pattern = r"\b(EC2|S3|RDS|Lambda|VPC|ALB|ELB|DynamoDB|SNS|SQS|CloudFront|Route53)\b"
        detected_resources = list(set(re.findall(resource_pattern, response, re.IGNORECASE)))
        
        # Extract explanation (everything not in code blocks)
        explanation = re.sub(r"```.*?```", "", response, flags=re.DOTALL).strip()
        
        return {
            "code": code,
            "explanation": explanation,
            "detected_resources": detected_resources,
            "format": output_format,
            "raw_response": response
        }
"""
Input validation utilities for Arch-I-Tect.

This module provides validation functions for file uploads, environment
configuration, and other input data.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import io

from loguru import logger


def validate_environment() -> None:
    """
    Validate that all required environment variables are set.
    
    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = [
        "LLM_PROVIDER",
        "MAX_IMAGE_SIZE_MB",
        "ALLOWED_IMAGE_TYPES"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    # Validate LLM provider configuration
    llm_provider = os.getenv("LLM_PROVIDER", "").lower()
    
    if llm_provider == "ollama":
        if not os.getenv("OLLAMA_BASE_URL"):
            raise ValueError("OLLAMA_BASE_URL is required when using Ollama provider")
        if not os.getenv("OLLAMA_MODEL"):
            raise ValueError("OLLAMA_MODEL is required when using Ollama provider")
            
    elif llm_provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
            
    elif llm_provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
            
    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {llm_provider}. "
            "Must be one of: ollama, openai, anthropic"
        )
    
    logger.info(f"Environment validated. Using {llm_provider} as LLM provider.")


def validate_image_file(
    file_content: bytes,
    filename: str
) -> Tuple[bool, Optional[str], Optional[dict]]:
    """
    Validate an uploaded image file.
    
    Args:
        file_content: Raw file content in bytes
        filename: Original filename
        
    Returns:
        Tuple of (is_valid, error_message, metadata)
        - is_valid: Whether the file is valid
        - error_message: Error message if invalid, None otherwise
        - metadata: Dictionary with image metadata if valid
    """
    # Check file size
    max_size_mb = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    file_size_mb = len(file_content) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)", None
    
    # Check file extension
    allowed_types = os.getenv("ALLOWED_IMAGE_TYPES", "png,jpg,jpeg,webp").split(",")
    file_ext = Path(filename).suffix.lower().strip(".")
    
    if file_ext not in allowed_types:
        return False, f"File type '{file_ext}' not allowed. Allowed types: {', '.join(allowed_types)}", None
    
    # Validate image content
    try:
        image = Image.open(io.BytesIO(file_content))
        
        # Extract metadata
        metadata = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "file_size_mb": file_size_mb
        }
        
        # Check minimum dimensions
        min_dimension = 100
        if image.width < min_dimension or image.height < min_dimension:
            return False, f"Image too small. Minimum dimension: {min_dimension}px", None
        
        # Check maximum dimensions
        max_dimension = 4096
        if image.width > max_dimension or image.height > max_dimension:
            return False, f"Image too large. Maximum dimension: {max_dimension}px", None
        
        logger.info(f"Image validated: {filename} ({image.width}x{image.height})")
        return True, None, metadata
        
    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")
        return False, "Invalid image file or corrupted content", None


def validate_llm_response(response: str, expected_format: str = "terraform") -> Tuple[bool, Optional[str]]:
    """
    Validate LLM-generated code response.
    
    Args:
        response: Raw response from LLM
        expected_format: Expected code format (terraform, cloudformation)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    assert response, "Response cannot be empty"
    assert expected_format in ["terraform", "cloudformation"], f"Invalid format: {expected_format}"
    
    # Check if response contains code blocks
    if "```" not in response:
        return False, "Response does not contain code blocks"
    
    # Basic validation based on format
    if expected_format == "terraform":
        # Check for basic Terraform syntax indicators
        terraform_keywords = ["resource", "provider", "variable", "output"]
        has_terraform_syntax = any(keyword in response.lower() for keyword in terraform_keywords)
        
        if not has_terraform_syntax:
            return False, "Response does not appear to contain valid Terraform code"
            
    elif expected_format == "cloudformation":
        # Check for basic CloudFormation syntax indicators
        cf_keywords = ["AWSTemplateFormatVersion", "Resources", "Type:", "Properties:"]
        has_cf_syntax = any(keyword in response for keyword in cf_keywords)
        
        if not has_cf_syntax:
            return False, "Response does not appear to contain valid CloudFormation code"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove any path components
    filename = Path(filename).name
    
    # Replace problematic characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename
"""
Image processing service for Arch-I-Tect.

This module handles image preprocessing, enhancement, and preparation
for LLM analysis.
"""

import base64
from pathlib import Path
from typing import Dict, Tuple, Optional
import io

from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from loguru import logger


class ImageProcessor:
    """
    Service for processing cloud architecture diagram images.
    
    This class provides methods to preprocess images for better LLM recognition,
    including resizing, contrast enhancement, and format conversion.
    """
    
    def __init__(self):
        """Initialize the image processor with default settings."""
        self.max_dimension = 2048  # Maximum width or height
        self.target_format = "PNG"
        self.jpeg_quality = 95
        
    def preprocess_image(self, image_path: Path, image_id: str) -> Path:
        """
        Preprocess an image for optimal LLM analysis.
        
        Args:
            image_path: Path to the original image
            image_id: Unique identifier for the image
            
        Returns:
            Path: Path to the processed image
        """
        try:
            # Open the image
            with Image.open(image_path) as img:
                logger.info(f"Processing image: {image_path.name} ({img.size})")
                
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                    logger.debug(f"Converted image mode from {img.mode} to RGB")
                
                # Apply preprocessing steps
                img = self._resize_image(img)
                img = self._enhance_image(img)
                img = self._remove_transparency(img)
                
                # Save processed image
                processed_path = image_path.parent / f"{image_id}_processed.png"
                img.save(processed_path, format=self.target_format, optimize=True)
                
                logger.info(f"Saved processed image: {processed_path.name}")
                return processed_path
                
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {str(e)}")
            raise
    
    def _resize_image(self, img: Image.Image) -> Image.Image:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            img: PIL Image object
            
        Returns:
            Image: Resized image
        """
        width, height = img.size
        
        if width <= self.max_dimension and height <= self.max_dimension:
            return img
        
        # Calculate new dimensions maintaining aspect ratio
        if width > height:
            new_width = self.max_dimension
            new_height = int(height * (self.max_dimension / width))
        else:
            new_height = self.max_dimension
            new_width = int(width * (self.max_dimension / height))
        
        # Use high-quality resampling
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.debug(f"Resized image from {img.size} to {resized.size}")
        
        return resized
    
    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """
        Enhance image contrast and sharpness for better recognition.
        
        Args:
            img: PIL Image object
            
        Returns:
            Image: Enhanced image
        """
        # Enhance contrast
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.2)  # Increase contrast by 20%
        
        # Enhance sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(1.1)  # Increase sharpness by 10%
        
        # Auto-contrast to normalize levels
        img = ImageOps.autocontrast(img, cutoff=1)
        
        logger.debug("Applied image enhancements")
        return img
    
    def _remove_transparency(self, img: Image.Image) -> Image.Image:
        """
        Remove transparency by compositing on white background.
        
        Args:
            img: PIL Image object
            
        Returns:
            Image: Image without transparency
        """
        if img.mode != 'RGBA':
            return img
        
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        
        logger.debug("Removed transparency from image")
        return background
    
    def image_to_base64(self, image_path: Path) -> str:
        """
        Convert an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Base64 encoded image
        """
        assert image_path.exists(), f"Image file not found: {image_path}"
        
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def extract_image_regions(self, img: Image.Image) -> list[Dict]:
        """
        Extract potential diagram regions from the image.
        
        This method attempts to identify distinct regions in the diagram
        that might represent different cloud resources or components.
        
        Args:
            img: PIL Image object
            
        Returns:
            list: List of region dictionaries with coordinates and characteristics
        """
        # Convert to grayscale for analysis
        gray = img.convert('L')
        img_array = np.array(gray)
        
        # Simple threshold to identify non-white regions
        threshold = 240  # Values below this are considered content
        content_mask = img_array < threshold
        
        # Find bounding box of content
        rows = np.any(content_mask, axis=1)
        cols = np.any(content_mask, axis=0)
        
        if not rows.any() or not cols.any():
            logger.warning("No content detected in image")
            return []
        
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        # Return main content region
        # In a more advanced implementation, this could use connected components
        # or other CV techniques to identify individual diagram elements
        regions = [{
            "id": "main",
            "bounds": {
                "x": int(x_min),
                "y": int(y_min),
                "width": int(x_max - x_min),
                "height": int(y_max - y_min)
            },
            "area": int((x_max - x_min) * (y_max - y_min)),
            "center": {
                "x": int((x_min + x_max) / 2),
                "y": int((y_min + y_max) / 2)
            }
        }]
        
        logger.debug(f"Identified {len(regions)} content regions")
        return regions
    
    def prepare_for_llm(self, image_path: Path) -> Dict:
        """
        Prepare an image for LLM analysis with all necessary metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: Image data and metadata ready for LLM processing
        """
        with Image.open(image_path) as img:
            # Get basic metadata
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
            
            # Extract regions
            regions = self.extract_image_regions(img)
            
            # Convert to base64
            base64_image = self.image_to_base64(image_path)
            
            return {
                "base64": base64_image,
                "metadata": metadata,
                "regions": regions,
                "mime_type": f"image/{img.format.lower()}" if img.format else "image/png"
            }
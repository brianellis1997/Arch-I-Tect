"""
API routes for the Arch-I-Tect application.

This module defines all HTTP endpoints for uploading images and generating
Infrastructure as Code from cloud architecture diagrams.
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

from services.image_processor import ImageProcessor
from services.iac_generator import IaCGenerator
from utils.validators import validate_image_file, sanitize_filename
from api.middleware import limiter

router = APIRouter()

# Initialize services
image_processor = ImageProcessor()
iac_generator = IaCGenerator()


class GenerateCodeRequest(BaseModel):
    """Request model for code generation."""
    image_id: str = Field(..., description="ID of the uploaded image")
    output_format: str = Field("terraform", description="Output format: terraform or cloudformation")
    include_explanation: bool = Field(True, description="Include explanation with the code")


class GenerateCodeResponse(BaseModel):
    """Response model for code generation."""
    code: str = Field(..., description="Generated Infrastructure as Code")
    explanation: Optional[str] = Field(None, description="Explanation of the generated code")
    detected_resources: list[str] = Field(..., description="List of detected cloud resources")
    format: str = Field(..., description="Output format used")


class UploadResponse(BaseModel):
    """Response model for image upload."""
    image_id: str = Field(..., description="Unique identifier for the uploaded image")
    filename: str = Field(..., description="Sanitized filename")
    metadata: dict = Field(..., description="Image metadata")
    preview_url: str = Field(..., description="URL to preview the image")


@router.post("/upload", response_model=UploadResponse)
@limiter.limit("10/minute")
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> UploadResponse:
    """
    Upload a cloud architecture diagram image.
    
    Args:
        file: Uploaded image file
        background_tasks: FastAPI background tasks
        
    Returns:
        UploadResponse: Upload details including image ID and metadata
        
    Raises:
        HTTPException: If file validation fails
    """
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to read file")
    
    # Validate file
    is_valid, error_message, metadata = validate_image_file(content, file.filename)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Generate unique ID and sanitize filename
    image_id = str(uuid.uuid4())
    safe_filename = sanitize_filename(file.filename)
    
    # Save file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{image_id}_{safe_filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"Saved uploaded file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Process image in background (preprocessing, thumbnail generation)
    background_tasks.add_task(
        image_processor.preprocess_image,
        file_path,
        image_id
    )
    
    return UploadResponse(
        image_id=image_id,
        filename=safe_filename,
        metadata=metadata,
        preview_url=f"/api/v1/preview/{image_id}"
    )


@router.post("/generate", response_model=GenerateCodeResponse)
@limiter.limit("5/minute")
async def generate_code(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """
    Generate Infrastructure as Code from an uploaded diagram.
    
    Args:
        request: Code generation request parameters
        
    Returns:
        GenerateCodeResponse: Generated code and metadata
        
    Raises:
        HTTPException: If image not found or generation fails
    """
    # Find the uploaded image
    upload_dir = Path("uploads")
    image_files = list(upload_dir.glob(f"{request.image_id}_*"))
    
    if not image_files:
        raise HTTPException(
            status_code=404,
            detail=f"Image with ID {request.image_id} not found"
        )
    
    image_path = image_files[0]
    
    # Validate output format
    if request.output_format not in ["terraform", "cloudformation"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid output format. Must be 'terraform' or 'cloudformation'"
        )
    
    try:
        # Generate code using the IaC generator service
        result = await iac_generator.generate_from_image(
            image_path=image_path,
            output_format=request.output_format,
            include_explanation=request.include_explanation
        )
        
        return GenerateCodeResponse(
            code=result["code"],
            explanation=result.get("explanation"),
            detected_resources=result["detected_resources"],
            format=request.output_format
        )
        
    except ValueError as e:
        logger.error(f"Code generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during code generation")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate code. Please try again."
        )


@router.get("/preview/{image_id}")
async def preview_image(image_id: str):
    """
    Get a preview/thumbnail of an uploaded image.
    
    Args:
        image_id: Unique identifier of the image
        
    Returns:
        FileResponse: Image file
        
    Raises:
        HTTPException: If image not found
    """
    # Find the uploaded image
    upload_dir = Path("uploads")
    image_files = list(upload_dir.glob(f"{image_id}_*"))
    
    if not image_files:
        raise HTTPException(
            status_code=404,
            detail=f"Image with ID {image_id} not found"
        )
    
    image_path = image_files[0]
    
    # Check if preprocessed version exists
    processed_path = upload_dir / f"{image_id}_processed.png"
    if processed_path.exists():
        image_path = processed_path
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=image_path,
        media_type="image/png",
        headers={"Cache-Control": "max-age=3600"}
    )


@router.get("/status/{image_id}")
async def check_status(image_id: str):
    """
    Check the processing status of an uploaded image.
    
    Args:
        image_id: Unique identifier of the image
        
    Returns:
        dict: Status information
    """
    # Check if original exists
    upload_dir = Path("uploads")
    original_files = list(upload_dir.glob(f"{image_id}_*"))
    
    if not original_files:
        raise HTTPException(
            status_code=404,
            detail=f"Image with ID {image_id} not found"
        )
    
    # Check if processed version exists
    processed_path = upload_dir / f"{image_id}_processed.png"
    is_processed = processed_path.exists()
    
    return {
        "image_id": image_id,
        "status": "processed" if is_processed else "processing",
        "original_exists": True,
        "processed_exists": is_processed
    }
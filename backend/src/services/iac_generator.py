"""
Infrastructure as Code generation service.

This module orchestrates the process of converting architecture diagrams
into Infrastructure as Code using configured LLM providers.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
import asyncio

from loguru import logger

from models.llm_interface import LLMInterface
from services.image_processor import ImageProcessor
from services.prompt_manager import PromptManager
from utils.validators import validate_llm_response


class IaCGenerator:
    """
    Service for generating Infrastructure as Code from architecture diagrams.
    
    This class coordinates between image processing, LLM providers, and
    prompt management to produce high-quality IaC output.
    """
    
    def __init__(self):
        """Initialize the IaC generator with configured LLM provider."""
        self.image_processor = ImageProcessor()
        self.prompt_manager = PromptManager()
        self.llm_client = self._initialize_llm_client()
        
    def _initialize_llm_client(self) -> LLMInterface:
        """
        Initialize the appropriate LLM client based on configuration.
        
        Returns:
            LLMInterface: Configured LLM client
            
        Raises:
            ValueError: If LLM provider is not properly configured
        """
        provider = os.getenv("LLM_PROVIDER", "").lower()
        
        if provider == "ollama":
            from models.ollama_client import OllamaClient
            return OllamaClient(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model_name=os.getenv("OLLAMA_MODEL")
            )
        elif provider == "openai":
            from models.api_client import OpenAIClient
            return OpenAIClient(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
            )
        elif provider == "anthropic":
            from models.api_client import AnthropicClient
            return AnthropicClient(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    async def generate_from_image(
        self,
        image_path: Path,
        output_format: str = "terraform",
        include_explanation: bool = True,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Infrastructure as Code from an architecture diagram image.
        
        Args:
            image_path: Path to the diagram image
            output_format: Desired output format (terraform/cloudformation)
            include_explanation: Whether to include architectural explanation
            additional_context: Optional additional requirements
            
        Returns:
            dict: Generated code and metadata
            
        Raises:
            ValueError: If generation fails or output is invalid
        """
        assert image_path.exists(), f"Image file not found: {image_path}"
        assert output_format in ["terraform", "cloudformation"], f"Invalid format: {output_format}"
        
        logger.info(f"Starting IaC generation for {image_path.name}")
        
        try:
            # Check if LLM is available
            if not await self.llm_client.is_available():
                raise ValueError("LLM service is not available")
            
            # Check if LLM supports images
            if not self.llm_client.supports_images():
                raise ValueError(f"{self.llm_client.provider_name} does not support image analysis")
            
            # Generate code using the LLM's built-in method
            result = await self.llm_client.analyze_architecture_diagram(
                image_path=image_path,
                output_format=output_format
            )
            
            # Validate the generated code
            is_valid, error_msg = validate_llm_response(
                result.get("raw_response", ""),
                output_format
            )
            
            if not is_valid:
                logger.warning(f"Initial generation validation failed: {error_msg}")
                # Attempt to refine the output
                result = await self._refine_output(result, error_msg, output_format)
            
            # Add explanation if not requested
            if not include_explanation:
                result["explanation"] = None
            
            # Post-process the code
            result["code"] = self._post_process_code(result["code"], output_format)
            
            logger.info(f"Successfully generated {output_format} code with {len(result['detected_resources'])} resources")
            return result
            
        except Exception as e:
            logger.error(f"IaC generation failed: {str(e)}")
            raise ValueError(f"Failed to generate Infrastructure as Code: {str(e)}")
    
    async def _refine_output(
        self,
        initial_result: Dict[str, Any],
        error_message: str,
        output_format: str
    ) -> Dict[str, Any]:
        """
        Attempt to refine LLM output based on validation errors.
        
        Args:
            initial_result: Initial generation result
            error_message: Validation error message
            output_format: Target IaC format
            
        Returns:
            dict: Refined result
        """
        logger.info("Attempting to refine LLM output")
        
        refinement_prompt = self.prompt_manager.create_refinement_prompt(
            original_code=initial_result.get("code", ""),
            feedback=error_message,
            output_format=output_format
        )
        
        # Create a simple text-only refinement request
        from models.llm_interface import LLMResponse
        
        response = await self.llm_client.generate(
            prompt=refinement_prompt,
            temperature=0.1,
            max_tokens=4000
        )
        
        # Parse the refined response
        refined_result = self.llm_client._parse_architecture_response(
            response.content,
            output_format
        )
        
        # Merge with original result, keeping detected resources
        refined_result["detected_resources"] = initial_result.get("detected_resources", [])
        
        return refined_result
    
    def _post_process_code(self, code: str, output_format: str) -> str:
        """
        Post-process generated code for formatting and cleanup.
        
        Args:
            code: Generated code
            output_format: Code format
            
        Returns:
            str: Cleaned and formatted code
        """
        if not code:
            return ""
        
        # Remove any markdown formatting that might have leaked through
        code = code.strip()
        if code.startswith("```"):
            lines = code.split("\n")
            if len(lines) > 2:
                code = "\n".join(lines[1:-1])
        
        # Format-specific processing
        if output_format == "terraform":
            code = self._format_terraform_code(code)
        elif output_format == "cloudformation":
            code = self._format_cloudformation_code(code)
        
        return code
    
    def _format_terraform_code(self, code: str) -> str:
        """
        Apply Terraform-specific formatting.
        
        Args:
            code: Terraform HCL code
            
        Returns:
            str: Formatted code
        """
        # Ensure consistent indentation (2 spaces)
        lines = code.split("\n")
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Decrease indent for closing braces
            if stripped.startswith("}"):
                indent_level = max(0, indent_level - 1)
            
            # Apply indentation
            if stripped:
                formatted_lines.append("  " * indent_level + stripped)
            else:
                formatted_lines.append("")
            
            # Increase indent for opening braces
            if stripped.endswith("{"):
                indent_level += 1
        
        return "\n".join(formatted_lines)
    
    def _format_cloudformation_code(self, code: str) -> str:
        """
        Apply CloudFormation-specific formatting.
        
        Args:
            code: CloudFormation YAML
            
        Returns:
            str: Formatted code
        """
        # For YAML, we'll trust the LLM's formatting
        # but ensure consistent line endings
        return code.replace("\r\n", "\n").strip()
    
    async def identify_resources(self, image_path: Path) -> list[str]:
        """
        Identify cloud resources in an architecture diagram.
        
        Args:
            image_path: Path to the diagram image
            
        Returns:
            list: Detected cloud resource types
        """
        from models.llm_interface import ImageInput
        
        # Prepare image
        image_data = self.image_processor.prepare_for_llm(image_path)
        image_input = ImageInput(
            base64=image_data["base64"],
            mime_type=image_data["mime_type"]
        )
        
        # Get identification prompt
        prompt = self.prompt_manager.get_resource_identification_prompt()
        
        # Query LLM
        response = await self.llm_client.generate(
            prompt=prompt,
            images=[image_input],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Extract resource types from response
        import re
        resource_pattern = r"\b(EC2|S3|RDS|Lambda|VPC|ALB|ELB|DynamoDB|SNS|SQS|CloudFront|Route53|ECS|EKS|API Gateway|Kinesis|Redshift|ElastiCache|Neptune|Athena|Glue|Step Functions|EventBridge|Cognito|Secrets Manager|Systems Manager|CloudWatch|CloudTrail|WAF|Shield|GuardDuty|Inspector|Macie|Config|Organizations|Control Tower|Service Catalog|AppSync|Amplify|Elastic Beanstalk|Fargate|Batch|SageMaker|Comprehend|Rekognition|Polly|Transcribe|Translate|Lex|Personalize|Forecast|Textract|Kendra|QuickSight|Managed Blockchain|Quantum Ledger|Ground Station|RoboMaker|IoT Core|IoT Analytics|IoT Events|IoT Things Graph|IoT Device Defender|IoT Device Management|IoT 1-Click|IoT Greengrass|Timestream|DocumentDB|Keyspaces|QLDB|Managed Apache Cassandra|FSx|EFS|Storage Gateway|DataSync|Transfer Family|Backup|CloudEndure|Application Discovery|Migration Hub|Server Migration|Database Migration|Snow Family|Direct Connect|VPN|Transit Gateway|PrivateLink|Global Accelerator|CloudFront|Route 53|API Gateway|App Mesh|Cloud Map|X-Ray|CloudFormation|CDK|SAM|OpsWorks|Service Catalog|Control Tower|Organizations|Resource Access Manager|License Manager|Compute Optimizer|Trusted Advisor|Well-Architected Tool|Personal Health Dashboard)\b"
        
        resources = list(set(re.findall(resource_pattern, response.content, re.IGNORECASE)))
        
        logger.info(f"Identified {len(resources)} resource types in diagram")
        return resources
    
    async def explain_architecture(self, image_path: Path) -> str:
        """
        Generate a detailed explanation of an architecture diagram.
        
        Args:
            image_path: Path to the diagram image
            
        Returns:
            str: Architecture explanation
        """
        from models.llm_interface import ImageInput
        
        # Prepare image
        image_data = self.image_processor.prepare_for_llm(image_path)
        image_input = ImageInput(
            base64=image_data["base64"],
            mime_type=image_data["mime_type"]
        )
        
        # Get explanation prompt
        prompt = self.prompt_manager.get_explanation_prompt()
        
        # Query LLM
        response = await self.llm_client.generate(
            prompt=prompt,
            images=[image_input],
            temperature=0.3,  # Slightly higher for more creative explanations
            max_tokens=2000
        )
        
        return response.content
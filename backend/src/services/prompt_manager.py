"""
Prompt management for LLM interactions.

This module manages prompt templates and strategies for generating
Infrastructure as Code from architecture diagrams.
"""

from typing import Dict, Optional
from enum import Enum


class OutputFormat(Enum):
    """Supported Infrastructure as Code output formats."""
    TERRAFORM = "terraform"
    CLOUDFORMATION = "cloudformation"


class PromptManager:
    """
    Manages prompt templates for different LLM tasks.
    
    This class provides carefully crafted prompts for analyzing architecture
    diagrams and generating corresponding Infrastructure as Code.
    """
    
    def __init__(self):
        """Initialize the prompt manager with default templates."""
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """
        Load prompt templates for different scenarios.
        
        Returns:
            dict: Mapping of template names to prompt strings
        """
        return {
            "terraform_base": """You are an expert cloud architect and Infrastructure as Code specialist. 
Analyze the provided cloud architecture diagram and generate complete, production-ready Terraform code.

Instructions:
1. Carefully examine the diagram to identify all cloud resources and their relationships
2. Determine the cloud provider (AWS, Azure, GCP) from the diagram elements
3. Generate valid Terraform HCL code that accurately represents the architecture
4. Include the following in your code:
   - Provider configuration
   - All resources shown in the diagram
   - Proper resource dependencies and references
   - Variables for customizable values
   - Outputs for important resource attributes
   - Comments explaining the architecture

Guidelines:
- Use modern Terraform syntax (0.12+)
- Follow Terraform best practices for naming and organization
- Include resource tags for organization and cost tracking
- Ensure all resources are properly connected as shown in the diagram
- Add data sources where appropriate
- Include basic security groups/network ACLs as implied by the architecture

Output the Terraform code within ```hcl code blocks.
After the code, provide a brief explanation of the architecture and any assumptions made.""",

            "cloudformation_base": """You are an expert cloud architect and AWS CloudFormation specialist.
Analyze the provided cloud architecture diagram and generate complete, production-ready CloudFormation YAML.

Instructions:
1. Carefully examine the diagram to identify all AWS resources and their relationships
2. Generate valid CloudFormation YAML that accurately represents the architecture
3. Include the following in your template:
   - AWSTemplateFormatVersion and Description
   - Parameters for customizable values
   - All resources shown in the diagram
   - Proper resource dependencies using DependsOn or Ref/GetAtt
   - Outputs for important resource attributes
   - Metadata and comments explaining the architecture

Guidelines:
- Use CloudFormation best practices for organization
- Include resource tags for organization and cost tracking
- Ensure all resources are properly connected as shown in the diagram
- Add Conditions where appropriate for flexibility
- Include basic security groups and network ACLs as implied
- Use intrinsic functions effectively (Ref, GetAtt, Join, etc.)

Output the CloudFormation template within ```yaml code blocks.
After the code, provide a brief explanation of the architecture and any assumptions made.""",

            "resource_identification": """Analyze this cloud architecture diagram and identify all cloud resources present.

List each resource with:
1. Resource type (e.g., EC2, S3, RDS)
2. Approximate count if multiple instances
3. Key relationships or connections between resources
4. Any labels or text visible in the diagram

Be thorough and specific in your analysis.""",

            "architecture_explanation": """Based on this cloud architecture diagram, provide:

1. A high-level overview of the system architecture
2. The apparent purpose or use case of this infrastructure
3. Key architectural patterns employed (e.g., multi-tier, microservices, serverless)
4. Notable security or networking considerations
5. Potential areas for improvement or optimization

Keep your explanation concise but comprehensive."""
        }
    
    def get_architecture_prompt(
        self,
        output_format: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Get the appropriate prompt for architecture analysis.
        
        Args:
            output_format: Desired output format (terraform/cloudformation)
            additional_context: Optional additional context or requirements
            
        Returns:
            str: Complete prompt for the LLM
        """
        # Select base template
        if output_format.lower() == "terraform":
            base_prompt = self.templates["terraform_base"]
        elif output_format.lower() == "cloudformation":
            base_prompt = self.templates["cloudformation_base"]
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Add additional context if provided
        if additional_context:
            base_prompt += f"\n\nAdditional Requirements:\n{additional_context}"
        
        return base_prompt
    
    def get_resource_identification_prompt(self) -> str:
        """
        Get prompt for identifying resources in a diagram.
        
        Returns:
            str: Resource identification prompt
        """
        return self.templates["resource_identification"]
    
    def get_explanation_prompt(self) -> str:
        """
        Get prompt for explaining an architecture.
        
        Returns:
            str: Architecture explanation prompt
        """
        return self.templates["architecture_explanation"]
    
    def create_refinement_prompt(
        self,
        original_code: str,
        feedback: str,
        output_format: str
    ) -> str:
        """
        Create a prompt for refining generated code based on feedback.
        
        Args:
            original_code: Previously generated code
            feedback: User feedback or error messages
            output_format: Target format (terraform/cloudformation)
            
        Returns:
            str: Refinement prompt
        """
        return f"""Please refine the following {output_format.upper()} code based on the feedback provided.

Original Code:
```
{original_code}
```

Feedback:
{feedback}

Generate an improved version that addresses the feedback while maintaining all the original functionality.
Ensure the code remains valid and follows best practices.

Output the refined code within appropriate code blocks."""
    
    def create_conversion_prompt(
        self,
        source_code: str,
        source_format: str,
        target_format: str
    ) -> str:
        """
        Create a prompt for converting between IaC formats.
        
        Args:
            source_code: Source Infrastructure as Code
            source_format: Source format (e.g., terraform)
            target_format: Target format (e.g., cloudformation)
            
        Returns:
            str: Conversion prompt
        """
        return f"""Convert the following {source_format.upper()} code to {target_format.upper()}.

Source {source_format.upper()} Code:
```
{source_code}
```

Requirements:
1. Maintain all resources and their configurations
2. Preserve all relationships and dependencies
3. Convert variable/parameter definitions appropriately
4. Adapt outputs to the target format
5. Ensure the converted code is valid and follows {target_format} best practices

Output the converted code within appropriate code blocks."""
    
    def enhance_prompt_with_examples(
        self,
        base_prompt: str,
        resource_types: list[str]
    ) -> str:
        """
        Enhance a prompt with specific examples for detected resources.
        
        Args:
            base_prompt: Base prompt to enhance
            resource_types: List of detected resource types
            
        Returns:
            str: Enhanced prompt with examples
        """
        if not resource_types:
            return base_prompt
        
        examples = []
        
        # Add specific guidance for common resources
        resource_guidance = {
            "EC2": "Include instance type, AMI, security groups, and key pair",
            "RDS": "Include engine, instance class, storage, and backup configuration",
            "S3": "Include bucket policies, versioning, and lifecycle rules",
            "Lambda": "Include runtime, handler, timeout, and memory settings",
            "VPC": "Include CIDR blocks, subnets, route tables, and gateways",
            "ALB": "Include target groups, listeners, and health checks",
            "ECS": "Include task definitions, services, and cluster configuration"
        }
        
        for resource in resource_types:
            if resource.upper() in resource_guidance:
                examples.append(f"- {resource}: {resource_guidance[resource.upper()]}")
        
        if examples:
            enhancement = "\n\nFor the detected resources, ensure you include:\n" + "\n".join(examples)
            return base_prompt + enhancement
        
        return base_prompt
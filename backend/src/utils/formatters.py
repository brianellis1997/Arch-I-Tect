"""
Code formatting utilities for Infrastructure as Code output.

This module provides formatting and validation helpers for Terraform
and CloudFormation code.
"""

import re
import json
from typing import Dict, Tuple, Optional
from loguru import logger


class CodeFormatter:
    """
    Formatter for Infrastructure as Code output.
    
    Provides methods to format, validate, and clean IaC code
    for better readability and correctness.
    """
    
    @staticmethod
    def extract_code_block(text: str, language: Optional[str] = None) -> str:
        """
        Extract code from markdown code blocks.
        
        Args:
            text: Text potentially containing code blocks
            language: Optional language identifier to match
            
        Returns:
            str: Extracted code or original text if no blocks found
        """
        # Pattern for code blocks with optional language
        if language:
            pattern = rf"```{language}\n(.*?)```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)```"
        
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the first match
            return matches[0].strip()
        
        # Try without language specifier
        pattern = r"```\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Return original text if no code blocks found
        return text.strip()
    
    @staticmethod
    def format_terraform(code: str) -> str:
        """
        Format Terraform HCL code for consistency.
        
        Args:
            code: Raw Terraform code
            
        Returns:
            str: Formatted code
        """
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        in_heredoc = False
        heredoc_marker = None
        
        for line in lines:
            stripped = line.strip()
            
            # Handle heredoc strings
            if not in_heredoc and '<<' in line:
                heredoc_match = re.search(r'<<(\w+)', line)
                if heredoc_match:
                    in_heredoc = True
                    heredoc_marker = heredoc_match.group(1)
                    formatted_lines.append('  ' * indent_level + stripped)
                    continue
            
            if in_heredoc:
                formatted_lines.append(line)  # Preserve heredoc content as-is
                if stripped == heredoc_marker:
                    in_heredoc = False
                    heredoc_marker = None
                continue
            
            # Skip empty lines
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}') or stripped.startswith(']'):
                indent_level = max(0, indent_level - 1)
            
            # Add the line with proper indentation
            formatted_lines.append('  ' * indent_level + stripped)
            
            # Increase indent for opening braces
            if stripped.endswith('{') or stripped.endswith('['):
                indent_level += 1
            
            # Handle single-line blocks
            if '{' in stripped and '}' in stripped:
                # Don't change indent for single-line blocks
                pass
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_cloudformation(code: str) -> str:
        """
        Format CloudFormation YAML for consistency.
        
        Args:
            code: Raw CloudFormation YAML
            
        Returns:
            str: Formatted code
        """
        # For YAML, we'll do minimal formatting to preserve structure
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Ensure consistent spacing after colons
            if ':' in line and not line.strip().endswith(':'):
                # Add space after colon if missing
                line = re.sub(r':(?! )', ': ', line)
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def validate_terraform_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        Basic syntax validation for Terraform code.
        
        Args:
            code: Terraform HCL code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for balanced braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        if open_braces != close_braces:
            return False, f"Unbalanced braces: {open_braces} open, {close_braces} close"
        
        # Check for required Terraform blocks
        if 'resource' not in code and 'data' not in code and 'module' not in code:
            return False, "No resources, data sources, or modules defined"
        
        # Check for basic syntax patterns
        resource_pattern = r'resource\s+"[\w-]+"\s+"[\w-]+"'
        if 'resource' in code and not re.search(resource_pattern, code):
            return False, "Invalid resource declaration syntax"
        
        # Check for unclosed quotes
        quote_count = code.count('"') - code.count('\\"')
        if quote_count % 2 != 0:
            return False, "Unclosed quotes detected"
        
        return True, None
    
    @staticmethod
    def validate_cloudformation_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        Basic syntax validation for CloudFormation YAML.
        
        Args:
            code: CloudFormation YAML
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required top-level keys
        required_keys = ['AWSTemplateFormatVersion', 'Resources']
        
        for key in required_keys:
            if key not in code:
                return False, f"Missing required key: {key}"
        
        # Check basic YAML structure
        if not code.strip().startswith('AWSTemplateFormatVersion:'):
            return False, "Template must start with AWSTemplateFormatVersion"
        
        # Check for basic indentation consistency
        lines = code.split('\n')
        indent_pattern = re.compile(r'^(\s*)')
        indents = set()
        
        for line in lines:
            if line.strip():
                match = indent_pattern.match(line)
                if match:
                    indent = len(match.group(1))
                    if indent > 0:
                        indents.add(indent)
        
        # Check if indents are multiples of 2 (common YAML style)
        if indents and not all(indent % 2 == 0 for indent in indents):
            logger.warning("Inconsistent indentation detected in CloudFormation template")
        
        return True, None
    
    @staticmethod
    def add_header_comment(code: str, format_type: str) -> str:
        """
        Add a header comment to generated code.
        
        Args:
            code: Generated code
            format_type: Type of code (terraform/cloudformation)
            
        Returns:
            str: Code with header comment
        """
        if format_type.lower() == "terraform":
            header = """# Generated by Arch-I-Tect
# This Terraform configuration was automatically generated from an architecture diagram.
# Please review and modify as needed before applying.

"""
        else:  # CloudFormation
            header = """# Generated by Arch-I-Tect
# This CloudFormation template was automatically generated from an architecture diagram.
# Please review and modify as needed before deploying.

"""
        
        return header + code
    
    @staticmethod
    def extract_resources_from_code(code: str, format_type: str) -> list[str]:
        """
        Extract resource types from generated code.
        
        Args:
            code: IaC code
            format_type: Code format (terraform/cloudformation)
            
        Returns:
            list: Detected resource types
        """
        resources = []
        
        if format_type.lower() == "terraform":
            # Extract Terraform resource types
            pattern = r'resource\s+"([\w-]+)"'
            matches = re.findall(pattern, code)
            resources.extend(matches)
            
            # Also check data sources
            data_pattern = r'data\s+"([\w-]+)"'
            data_matches = re.findall(data_pattern, code)
            resources.extend([f"data.{match}" for match in data_matches])
            
        else:  # CloudFormation
            # Extract CloudFormation resource types
            pattern = r'Type:\s*["\']?(AWS::\w+::\w+)'
            matches = re.findall(pattern, code)
            resources.extend(matches)
        
        # Remove duplicates and return
        return list(set(resources))
    
    @staticmethod
    def sanitize_resource_name(name: str) -> str:
        """
        Sanitize resource names for IaC compatibility.
        
        Args:
            name: Original resource name
            
        Returns:
            str: Sanitized name
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'resource_' + sanitized
        
        # Limit length
        max_length = 63  # Common limit for many cloud resources
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized or 'resource'
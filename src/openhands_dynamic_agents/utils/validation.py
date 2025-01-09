"""
Input validation utilities for dynamic agents.
"""

from typing import Dict, Any
from .result import OperationResult

def validate_input(data: Dict[str, Any]) -> OperationResult[bool]:
    """
    Validate input data for dynamic agents.
    
    Args:
        data: Input data dictionary
        
    Returns:
        OperationResult indicating validation success/failure
    """
    if not isinstance(data, dict):
        return OperationResult.error(
            "Input must be a dictionary",
            error_type="ValidationError",
            details={"type": type(data).__name__}
        )
    
    # Add specific validation rules based on agent requirements
    required_fields = []
    missing_fields = [f for f in required_fields if f not in data]
    
    if missing_fields:
        return OperationResult.error(
            f"Missing required fields: {', '.join(missing_fields)}",
            error_type="ValidationError",
            details={"missing_fields": missing_fields}
        )
    
    return OperationResult.success(True)
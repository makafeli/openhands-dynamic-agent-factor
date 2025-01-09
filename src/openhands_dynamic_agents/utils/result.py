"""
Result types for operations.
"""

from typing import TypeVar, Generic, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T')

@dataclass
class OperationError:
    """Error information for operations."""
    message: str
    error_type: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "message": self.message,
            "type": self.error_type,
            "details": self.details,
            "timestamp": datetime.now().isoformat()
        }

@dataclass
class OperationResult(Generic[T]):
    """
    Generic result type for operations.
    
    Attributes:
        success: Whether the operation succeeded
        data: Result data if successful
        error: Error information if failed
        metadata: Optional metadata about the operation
    """
    success: bool
    data: Optional[T] = None
    error: Optional[OperationError] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success(
        cls,
        data: T,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'OperationResult[T]':
        """Create a successful result."""
        return cls(
            success=True,
            data=data,
            metadata=metadata
        )
    
    @classmethod
    def error(
        cls,
        message: str,
        error_type: str = "Error",
        details: Optional[Dict[str, Any]] = None
    ) -> 'OperationResult[T]':
        """Create an error result."""
        return cls(
            success=False,
            error=OperationError(
                message=message,
                error_type=error_type,
                details=details
            )
        )
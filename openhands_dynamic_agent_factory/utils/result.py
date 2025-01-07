"""Operation result handling for the OpenHands Dynamic Agent Factory."""
from typing import Any, Optional

class OperationResult:
    """Represents the result of an operation."""
    def __init__(self, 
                 success: bool, 
                 data: Any = None, 
                 error: Optional[str] = None,
                 error_type: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.error_type = error_type
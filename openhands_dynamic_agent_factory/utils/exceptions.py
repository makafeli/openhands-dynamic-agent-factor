"""Custom exceptions for the OpenHands Dynamic Agent Factory."""

class TechAnalyzerError(Exception):
    """Base exception for technology analyzer errors."""
    def __init__(self, message: str, error_type: str, details: dict = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
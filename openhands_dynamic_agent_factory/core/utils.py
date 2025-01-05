"""
Shared utilities and base classes for the dynamic agent factory system.
Provides common functionality, error handling, and performance optimizations.
"""

import functools
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, Optional, TypeVar, Generic, Union
from abc import ABC, abstractmethod

# Type variables for generics
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseError(Exception):
    """Base error class with enhanced context and recovery hints."""
    def __init__(
        self,
        message: str,
        error_type: str,
        details: Optional[Dict[str, Any]] = None,
        recovery_hint: Optional[str] = None
    ):
        self.error_type = error_type
        self.details = details or {}
        self.recovery_hint = recovery_hint
        self.timestamp = datetime.now()
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error_type": self.error_type,
            "message": str(self),
            "details": self.details,
            "recovery_hint": self.recovery_hint,
            "timestamp": self.timestamp.isoformat()
        }

class ValidationError(BaseError):
    """Validation error with context."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            "ValidationError",
            details,
            "Check input requirements and constraints"
        )

class StateError(BaseError):
    """State management error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            "StateError",
            details,
            "Verify state file integrity and permissions"
        )

@dataclass
class OperationResult(Generic[T]):
    """Generic operation result with metadata."""
    success: bool
    data: Optional[T] = None
    error: Optional[BaseError] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = None

class Cache(Generic[K, V]):
    """Thread-safe cache with TTL support."""
    
    def __init__(self, ttl: int = 3600):
        """Initialize cache with TTL in seconds."""
        self._cache: Dict[K, Dict[str, Any]] = {}
        self._lock = Lock()
        self.ttl = ttl

    def get(self, key: K) -> Optional[V]:
        """Get value from cache with TTL check."""
        with self._lock:
            if key not in self._cache:
                return None
                
            entry = self._cache[key]
            if time.time() - entry['timestamp'] > self.ttl:
                del self._cache[key]
                return None
                
            return entry['value']

    def set(self, key: K, value: V) -> None:
        """Set cache value with timestamp."""
        with self._lock:
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

class StateManager(Generic[T]):
    """Generic state manager with atomic operations."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.lock = Lock()
        self._ensure_state_file()

    def _ensure_state_file(self) -> None:
        """Ensure state file exists with valid structure."""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.save_state({
                "data": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            })

    def load_state(self) -> OperationResult[T]:
        """Load state with validation."""
        with self.lock:
            try:
                start_time = time.time()
                content = self.state_file.read_text(encoding='utf-8')
                state = json.loads(content)
                
                # Validate state structure
                if not isinstance(state, dict) or 'data' not in state:
                    raise ValidationError("Invalid state structure")
                
                duration = time.time() - start_time
                return OperationResult(
                    success=True,
                    data=state['data'],
                    duration=duration,
                    metadata=state.get('metadata', {})
                )
                
            except Exception as e:
                return OperationResult(
                    success=False,
                    error=StateError(f"Failed to load state: {str(e)}")
                )

    def save_state(self, state: Dict[str, Any]) -> OperationResult[bool]:
        """Save state atomically with backup."""
        with self.lock:
            backup_file = self.state_file.with_suffix('.backup')
            start_time = time.time()
            
            try:
                # Create backup
                if self.state_file.exists():
                    self.state_file.rename(backup_file)
                
                # Update metadata
                state['metadata'] = {
                    **(state.get('metadata', {})),
                    'last_updated': datetime.now().isoformat()
                }
                
                # Write new state
                with self.state_file.open('w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
                
                # Remove backup
                if backup_file.exists():
                    backup_file.unlink()
                
                duration = time.time() - start_time
                return OperationResult(
                    success=True,
                    data=True,
                    duration=duration,
                    metadata=state['metadata']
                )
                
            except Exception as e:
                # Restore backup
                if backup_file.exists():
                    backup_file.rename(self.state_file)
                    
                return OperationResult(
                    success=False,
                    error=StateError(f"Failed to save state: {str(e)}")
                )

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt} failed: {str(e)}. "
                            f"Retrying in {current_delay:.1f}s"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    
            logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
            
        return wrapper
    return decorator

class Validator(ABC):
    """Abstract base class for validators."""
    
    @abstractmethod
    def validate(self, data: Any) -> OperationResult[bool]:
        """Validate data."""
        pass

class CodeValidator(Validator):
    """Code validator with security checks."""
    
    def __init__(self):
        self.forbidden_patterns = [
            (r"os\s*\.\s*system", "System command execution"),
            (r"subprocess", "Subprocess execution"),
            (r"eval\s*\(", "Code evaluation"),
            (r"exec\s*\(", "Code execution"),
            (r"__import__", "Dynamic imports"),
            (r"open\s*\(", "File operations"),
            (r"socket\.", "Network operations"),
            (r"requests?\.", "HTTP requests"),
            (r"urllib", "URL operations")
        ]

    def validate(self, code: str) -> OperationResult[bool]:
        """Validate code security."""
        import re
        start_time = time.time()
        
        try:
            for pattern, description in self.forbidden_patterns:
                if re.search(pattern, code):
                    return OperationResult(
                        success=False,
                        error=ValidationError(
                            f"Security violation: {description}",
                            {"pattern": pattern}
                        ),
                        duration=time.time() - start_time
                    )
            
            return OperationResult(
                success=True,
                data=True,
                duration=time.time() - start_time
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=ValidationError(f"Validation failed: {str(e)}")
            )

class StructureValidator(Validator):
    """Code structure validator."""
    
    def __init__(self, required_elements: Dict[str, str]):
        self.required_elements = required_elements

    def validate(self, code: str) -> OperationResult[bool]:
        """Validate code structure."""
        start_time = time.time()
        missing_elements = []
        
        for element, description in self.required_elements.items():
            if element not in code:
                missing_elements.append(description)
        
        if missing_elements:
            return OperationResult(
                success=False,
                error=ValidationError(
                    "Missing required elements",
                    {"missing": missing_elements}
                ),
                duration=time.time() - start_time
            )
        
        return OperationResult(
            success=True,
            data=True,
            duration=time.time() - start_time
        )

# Performance monitoring decorator
def monitor_performance(operation: str):
    """Monitor operation performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{operation} failed after {duration:.3f}s: {str(e)}"
                )
                raise
        return wrapper
    return decorator

"""
Monitoring utilities for dynamic agents.
"""

import time
import logging
import functools
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

def monitor_performance(operation_name: str = None):
    """
    Decorator to monitor function performance.
    
    Args:
        operation_name: Name of the operation being monitored
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            operation = operation_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"{operation} completed in {duration:.2f}s",
                    extra={
                        "operation": operation,
                        "duration": duration,
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{operation} failed after {duration:.2f}s: {e}",
                    extra={
                        "operation": operation,
                        "duration": duration,
                        "success": False,
                        "error": str(e)
                    }
                )
                raise
                
        return wrapper
    return decorator
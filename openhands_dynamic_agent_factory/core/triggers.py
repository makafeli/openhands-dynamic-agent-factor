"""
Trigger definitions and mappings for the dynamic agent factory.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TriggerInfo:
    """Data structure for trigger mapping information."""
    class_name: str
    description: str
    llm_prompt_template: str
    inputs: Optional[List[str]] = None
    outputs: Optional[List[str]] = None
    required_imports: Optional[List[str]] = None
    validation_rules: Optional[Dict] = None


# Expanded TRIGGER_MAP with comprehensive metadata

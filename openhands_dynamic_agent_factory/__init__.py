"""
OpenHands Dynamic Agent Factory

A module that provides dynamic agent generation capabilities for OpenHands.
"""

from .core.factory import DynamicAgentFactoryLLM, AgentGenerationError
from .core.triggers import TriggerInfo, TRIGGER_MAP

__version__ = "0.1.0"
__all__ = ['DynamicAgentFactoryLLM', 'AgentGenerationError', 'TriggerInfo', 'TRIGGER_MAP']
"""
Template management for technology stack analysis.
Handles loading, saving, and validation of analysis templates.
"""

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any, Optional, NoReturn
import re

@dataclass
class AnalysisTemplate:
    """Configuration template for technology analysis."""
    name: str
    description: str = ""
    use_cache: bool = True
    confidence_threshold: float = 0.7
    custom_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        """Validate template configuration."""
        self.validate()

    def validate(self) -> None:
        """Validate template configuration."""
        if not self.name:
            raise ValueError("Template name is required")

        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")

        # Validate custom patterns
        for pattern in self.custom_patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            **asdict(self),
            'type': 'tech_analysis_template',
            'schema_version': '1.0'
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisTemplate':
        """Create template from dictionary."""
        # Remove schema metadata
        template_data = {
            k: v for k, v in data.items()
            if k not in ['type', 'schema_version']
        }
        return cls(**template_data)

def save_template(template: AnalysisTemplate, path: Path) -> None:
    """Save template to file."""
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save atomically using temporary file
        temp_path = path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)
        temp_path.rename(path)

    except Exception as e:
        raise RuntimeError(f"Failed to save template: {str(e)}")

def load_template(path: Path) -> AnalysisTemplate:
    """Load template from file."""
    try:
        with open(path) as f:
            data = json.load(f)

        # Validate schema
        if data.get('type') != 'tech_analysis_template':
            raise ValueError("Invalid template type")

        schema_version = data.get('schema_version')
        if schema_version != '1.0':
            raise ValueError(f"Unsupported schema version: {schema_version}")

        return AnalysisTemplate.from_dict(data)

    except Exception as e:
        raise RuntimeError(f"Failed to load template: {str(e)}")

# Default templates with proper type hints
DEFAULT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    'strict': {
        'name': 'strict',
        'description': 'High confidence detection',
        'use_cache': True,
        'confidence_threshold': 0.9,
        'custom_patterns': [],
        'metadata': {},
        'version': '1.0.0'
    },
    'lenient': {
        'name': 'lenient',
        'description': 'Lenient detection',
        'use_cache': True,
        'confidence_threshold': 0.5,
        'custom_patterns': [],
        'metadata': {},
        'version': '1.0.0'
    },
    'custom': {
        'name': 'custom',
        'description': 'Template for detecting custom technologies',
        'use_cache': True,
        'confidence_threshold': 0.7,
        'custom_patterns': [
            r'\b(?:internal|custom|company)[-\s]*framework\b',
            r'\b(?:legacy|v\d+)[-\s]*framework\b'
        ],
        'metadata': {},
        'version': '1.0.0'
    }
}

def install_default_templates(templates_dir: Path) -> None:
    """Install default templates if they don't exist."""
    for template_data in DEFAULT_TEMPLATES.values():
        template_path = templates_dir / f"{template_data['name']}.json"
        if not template_path.exists():
            template = AnalysisTemplate(
                name=template_data['name'],
                description=template_data['description'],
                use_cache=template_data['use_cache'],
                confidence_threshold=template_data['confidence_threshold'],
                custom_patterns=template_data['custom_patterns'],
                metadata=template_data['metadata'],
                version=template_data['version']
            )
            save_template(template, template_path)

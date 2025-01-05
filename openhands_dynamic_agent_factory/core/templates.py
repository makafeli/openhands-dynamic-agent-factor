"""
Template management for CSS Framework Analyzer.
Handles loading, saving, and validation of analysis templates.
"""

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

@dataclass
class AnalysisTemplate:
    """Configuration template for framework analysis."""
    name: str
    description: str = ""
    use_cache: bool = True
    fallback_enabled: bool = True
    confidence_threshold: float = 0.7
    custom_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def __post_init__(self):
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
            'type': 'framework_analysis_template',
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
        if data.get('type') != 'framework_analysis_template':
            raise ValueError("Invalid template type")

        schema_version = data.get('schema_version')
        if schema_version != '1.0':
            raise ValueError(f"Unsupported schema version: {schema_version}")

        return AnalysisTemplate.from_dict(data)

    except Exception as e:
        raise RuntimeError(f"Failed to load template: {str(e)}")

class TemplateManager:
    """Manages analysis templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template manager."""
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates: Dict[str, AnalysisTemplate] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all templates from directory."""
        for path in self.templates_dir.glob("*.json"):
            try:
                template = load_template(path)
                self._templates[template.name] = template
            except Exception as e:
                print(f"Warning: Failed to load template {path}: {e}")

    def get_template(self, name: str) -> Optional[AnalysisTemplate]:
        """Get template by name."""
        return self._templates.get(name)

    def save_template(self, template: AnalysisTemplate) -> None:
        """Save template."""
        path = self.templates_dir / f"{template.name}.json"
        save_template(template, path)
        self._templates[template.name] = template

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates."""
        return [
            {
                'name': template.name,
                'description': template.description,
                'version': template.version,
                'custom_patterns': len(template.custom_patterns)
            }
            for template in self._templates.values()
        ]

    def delete_template(self, name: str) -> bool:
        """Delete template by name."""
        if name in self._templates:
            path = self.templates_dir / f"{name}.json"
            try:
                path.unlink()
                del self._templates[name]
                return True
            except Exception:
                return False
        return False

    def create_template(
        self,
        name: str,
        description: str = "",
        use_cache: bool = True,
        fallback_enabled: bool = True,
        confidence_threshold: float = 0.7,
        custom_patterns: Optional[List[str]] = None
    ) -> AnalysisTemplate:
        """Create new template."""
        template = AnalysisTemplate(
            name=name,
            description=description,
            use_cache=use_cache,
            fallback_enabled=fallback_enabled,
            confidence_threshold=confidence_threshold,
            custom_patterns=custom_patterns or []
        )
        self.save_template(template)
        return template

# Example templates
DEFAULT_TEMPLATES = {
    'strict': {
        'name': 'strict',
        'description': 'High confidence detection with no fallbacks',
        'use_cache': True,
        'fallback_enabled': False,
        'confidence_threshold': 0.9,
        'custom_patterns': []
    },
    'fuzzy': {
        'name': 'fuzzy',
        'description': 'Lenient detection with fallbacks',
        'use_cache': True,
        'fallback_enabled': True,
        'confidence_threshold': 0.5,
        'custom_patterns': []
    },
    'custom_frameworks': {
        'name': 'custom_frameworks',
        'description': 'Template for detecting custom/internal frameworks',
        'use_cache': True,
        'fallback_enabled': True,
        'confidence_threshold': 0.7,
        'custom_patterns': [
            r'\b(?:internal|custom|company)[-\s]*framework\b',
            r'\b(?:legacy|v\d+)[-\s]*framework\b'
        ]
    }
}

def install_default_templates(templates_dir: Path) -> None:
    """Install default templates if they don't exist."""
    for template_data in DEFAULT_TEMPLATES.values():
        template_path = templates_dir / f"{template_data['name']}.json"
        if not template_path.exists():
            template = AnalysisTemplate(**template_data)
            save_template(template, template_path)

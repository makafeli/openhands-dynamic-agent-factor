"""
Enhanced framework analyzer system that dynamically discovers and validates
various types of frameworks (CSS, UI, Testing, etc.).
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Set, cast
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import requests
from threading import Lock
from bs4 import BeautifulSoup

from .utils import BaseError, ValidationError, Cache, StateManager, OperationResult, monitor_performance
from .framework_sources import fetch_css_frameworks, fetch_ui_frameworks, fetch_testing_frameworks, fetch_github_info, fetch_npm_info

# Configure logging
logger = logging.getLogger(__name__)

class FrameworkAnalyzerError(BaseError):
    """Custom error for framework analysis operations."""
    def __init__(
        self,
        message: str,
        error_type: str,
        details: Optional[Dict[str, Any]] = None,
        recovery_hint: Optional[str] = None
    ):
        super().__init__(
            message,
            error_type,
            details,
            recovery_hint or "Check framework configuration and sources"
        )

@dataclass
class FrameworkInfo:
    """Enhanced data structure for framework information."""
    name: str
    type: str  # css, ui, testing, etc.
    category: str
    description: str
    tags: List[str] = field(default_factory=list)
    github_url: Optional[str] = None
    npm_package: Optional[str] = None
    stars: Optional[int] = None
    last_updated: Optional[datetime] = None
    validation_sources: List[str] = field(default_factory=list)
    discovery_context: Optional[str] = None
    is_validated: bool = False
    features: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    popularity_metrics: Dict[str, Any] = field(default_factory=dict)
    compatibility: Dict[str, List[str]] = field(default_factory=dict)
    version_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        data = asdict(self)
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameworkInfo':
        """Create from dictionary."""
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

class FrameworkAnalyzer:
    """
    Enhanced analyzer that discovers and validates frameworks from
    multiple authoritative sources.
    
    Features:
    - Framework detection with support for multiple types (CSS, UI, Testing)
    - Caching of framework data with configurable update intervals
    - Detailed error logging and fallback mechanisms
    - Performance optimizations for large-scale analysis
    - Interactive CLI and web dashboard support
    
    Example:
        ```python
        # Basic usage
        analyzer = FrameworkAnalyzer()
        results = analyzer.process_text("Building a site with Tailwind CSS")
        
        # With custom configuration
        analyzer = FrameworkAnalyzer(
            framework_types=["css", "ui"],
            update_interval_hours=12,
            cache_enabled=True,
            max_cache_size=1000,
            log_level=logging.DEBUG
        )
        ```
    """

    def __init__(
        self,
        framework_types: Optional[List[str]] = None,
        update_interval_hours: int = 24,
        cache_enabled: bool = True,
        max_cache_size: int = 1000,
        log_level: int = logging.INFO,
        state_dir: Optional[Path] = None
    ):
        """
        Initialize the analyzer with enhanced source checking.
        
        Args:
            framework_types: List of framework types to analyze (e.g., ["css", "ui"])
            update_interval_hours: Hours between framework database updates
            cache_enabled: Whether to enable result caching
            max_cache_size: Maximum number of cached results
            log_level: Logging level
            state_dir: Directory for state files
        """
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Initialize configuration
        self.framework_types = framework_types or ["css", "ui", "testing"]
        self.update_interval_hours = update_interval_hours
        self.cache_enabled = cache_enabled
        self.max_cache_size = max_cache_size
        
        # Initialize state management
        state_dir = state_dir or Path("/tmp/framework_analyzer")
        self.state_manager = StateManager[Dict[str, Any]](
            state_dir / "framework_state.json"
        )
        
        # Initialize caches
        self.results_cache = Cache[str, Dict[str, Any]](ttl=3600)
        self.framework_cache = Cache[str, FrameworkInfo](ttl=3600)
        
        # Framework variations for different types
        self.framework_variations = {
            "css": {
                'tailwind': ['tailwind', 'tailwindcss', 'tailwind-css'],
                'bootstrap': ['bootstrap', 'bootstrapui', 'bootstrap-ui'],
                'bulma': ['bulma', 'bulmacss', 'bulma-css']
            },
            "ui": {
                'react': ['react', 'reactjs', 'react.js'],
                'vue': ['vue', 'vuejs', 'vue.js'],
                'angular': ['angular', 'angularjs', 'angular.js']
            },
            "testing": {
                'jest': ['jest', 'jestjs', 'jest.js'],
                'mocha': ['mocha', 'mochajs', 'mocha.js'],
                'pytest': ['pytest', 'py.test']
            }
        }
        
        # Build reverse lookup for variations
        self.variation_lookup = {}
        for ftype, variations in self.framework_variations.items():
            for standard, variants in variations.items():
                for variant in variants:
                    self.variation_lookup[variant] = (ftype, standard)
        
        # Initialize framework database
        self.frameworks: Dict[str, FrameworkInfo] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load state with validation."""
        result = self.state_manager.load_state()
        if result.success and result.data:
            self.frameworks = {
                k: FrameworkInfo.from_dict(v)
                for k, v in result.data.get("frameworks", {}).items()
            }
            self.last_updated = datetime.fromisoformat(
                result.data.get("last_updated", "2000-01-01T00:00:00")
            )
        else:
            logger.warning("Failed to load state, initializing empty database")
            self.frameworks = {}
            self.last_updated = datetime(2000, 1, 1)  # Force update
            self._update_framework_database()

    def _save_state(self) -> None:
        """Save state atomically."""
        state = {
            "frameworks": {
                k: v.to_dict() for k, v in self.frameworks.items()
            },
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self.state_manager.save_state(state)

    @monitor_performance("Framework database update")
    def _update_framework_database(self) -> None:
        """Update framework database from all sources."""
        try:
            # Fetch from all sources based on framework types
            all_frameworks: List[Dict[str, Any]] = []
            
            if "css" in self.framework_types:
                all_frameworks.extend(fetch_css_frameworks())
            if "ui" in self.framework_types:
                all_frameworks.extend(fetch_ui_frameworks())
            if "testing" in self.framework_types:
                all_frameworks.extend(fetch_testing_frameworks())
            
            # Process each framework
            for framework_data in all_frameworks:
                name = framework_data["name"].strip().lower()
                
                if name not in self.frameworks:
                    # Create new framework entry
                    framework = FrameworkInfo(
                        name=framework_data["name"],
                        type=framework_data["type"],
                        category=framework_data["category"],
                        description=framework_data["description"],
                        github_url=framework_data.get("github_url"),
                        validation_sources=[framework_data["source"]],
                        is_validated=True,
                        last_updated=datetime.now()
                    )
                    
                    # Fetch additional information
                    if framework.github_url:
                        github_info = fetch_github_info(framework.github_url)
                        if github_info:
                            framework.stars = github_info["stars"]
                            framework.last_updated = github_info["last_updated"]
                            framework.popularity_metrics.update({
                                "github_stars": github_info["stars"],
                                "open_issues": github_info["open_issues"],
                                "forks": github_info["forks"]
                            })
                    
                    # Try to find npm package
                    npm_info = fetch_npm_info(name)
                    if npm_info:
                        framework.npm_package = npm_info["npm_package"]
                        framework.documentation_url = npm_info["homepage"]
                        framework.version_info = {
                            "latest": npm_info["latest_version"],
                            "versions": npm_info.get("versions", [])
                        }
                    
                    self.frameworks[name] = framework
                else:
                    # Update existing framework
                    framework = self.frameworks[name]
                    if framework_data["source"] not in framework.validation_sources:
                        framework.validation_sources.append(framework_data["source"])
                        framework.last_updated = datetime.now()

            self._save_state()
            logger.info(f"Framework database updated with {len(self.frameworks)} frameworks")

        except Exception as e:
            logger.error(f"Error updating framework database: {e}")
            raise FrameworkAnalyzerError(
                f"Database update failed: {str(e)}",
                "DatabaseUpdateError",
                {"error": str(e)}
            )

    def _normalize_framework_name(self, name: str) -> str:
        """Normalize framework name for consistent matching."""
        name = name.strip('*').strip().lower()
        
        # Check variation lookup
        for variation, (ftype, standard) in self.variation_lookup.items():
            if name == variation or name.startswith(f"{variation}-"):
                return standard
        
        return name

    @monitor_performance("Framework detection")
    def process_text(
        self,
        text: str,
        context: str = "",
        framework_types: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> OperationResult[Dict[str, Any]]:
        """
        Process text to identify framework references.
        
        Args:
            text: Input text to analyze
            context: Optional context about the text
            framework_types: Optional list of framework types to look for
            use_cache: Whether to use cached results
            
        Returns:
            OperationResult containing analysis results
        """
        try:
            # Check cache
            cache_key = f"{text}:{context}:{framework_types}"
            if self.cache_enabled and use_cache:
                cached = self.results_cache.get(cache_key)
                if cached:
                    return OperationResult(
                        success=True,
                        data=cached,
                        metadata={"cache_hit": True}
                    )
            
            # Initialize results
            results = {
                "identified_frameworks": [],
                "framework_types": framework_types or self.framework_types,
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            
            # Extract potential framework references
            text = text.lower()
            words = set(re.findall(r'\b\w+(?:[-\s]+\w+)*(?:[-\s]+(?:framework|lib))?\b', text))
            
            # Process each word
            seen_frameworks = set()
            for word in words:
                normalized = self._normalize_framework_name(word)
                if normalized in self.frameworks:
                    framework = self.frameworks[normalized]
                    
                    # Check framework type filter
                    if (framework_types and 
                        framework.type not in framework_types):
                        continue
                        
                    if normalized not in seen_frameworks:
                        seen_frameworks.add(normalized)
                        results["identified_frameworks"].append({
                            "name": framework.name,
                            "type": framework.type,
                            "category": framework.category,
                            "description": framework.description,
                            "confidence_score": self._calculate_confidence(word, normalized),
                            "popularity": framework.popularity_metrics,
                            "version_info": framework.version_info
                        })
            
            # Cache results
            if self.cache_enabled and use_cache:
                self.results_cache.set(cache_key, results)
            
            return OperationResult(
                success=True,
                data=results,
                metadata={
                    "cache_hit": False,
                    "framework_count": len(results["identified_frameworks"])
                }
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=FrameworkAnalyzerError(
                    f"Analysis failed: {str(e)}",
                    "AnalysisError",
                    {"text": text[:100], "error": str(e)}
                )
            )

    def _calculate_confidence(self, original: str, normalized: str) -> float:
        """Calculate confidence score for framework detection."""
        base_score = 0.7
        
        # Exact match bonus
        if original.lower() == normalized:
            base_score += 0.3
            
        # Known variation bonus
        if original in self.variation_lookup:
            base_score += 0.2
            
        return min(base_score, 1.0)

    def get_framework_info(
        self,
        name: str,
        include_alternatives: bool = False
    ) -> OperationResult[FrameworkInfo]:
        """Get detailed information about a framework."""
        try:
            normalized = self._normalize_framework_name(name)
            if normalized in self.frameworks:
                framework = self.frameworks[normalized]
                
                # Fetch alternatives if requested
                if include_alternatives:
                    framework.alternatives = self._find_alternatives(framework)
                    
                return OperationResult(
                    success=True,
                    data=framework
                )
                
            return OperationResult(
                success=False,
                error=FrameworkAnalyzerError(
                    f"Framework not found: {name}",
                    "FrameworkNotFound"
                )
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=FrameworkAnalyzerError(
                    f"Error fetching framework info: {str(e)}",
                    "InfoFetchError"
                )
            )

    def _find_alternatives(self, framework: FrameworkInfo) -> List[str]:
        """Find alternative frameworks of the same type."""
        alternatives = []
        for name, fw in self.frameworks.items():
            if (fw.type == framework.type and
                fw.name != framework.name and
                fw.category == framework.category):
                alternatives.append(fw.name)
        return alternatives

    def list_frameworks(
        self,
        framework_type: Optional[str] = None,
        category: Optional[str] = None,
        validated_only: bool = False,
        min_stars: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List frameworks with filtering.
        
        Args:
            framework_type: Optional framework type filter
            category: Optional category filter
            validated_only: Whether to only return validated frameworks
            min_stars: Minimum number of GitHub stars
        """
        frameworks = []
        for framework in self.frameworks.values():
            if framework_type and framework.type != framework_type:
                continue
            if category and framework.category != category:
                continue
            if validated_only and not framework.is_validated:
                continue
            if min_stars and (not framework.stars or framework.stars < min_stars):
                continue
            frameworks.append(framework.to_dict())
        return frameworks

    def get_categories(self, framework_type: Optional[str] = None) -> List[str]:
        """Get list of framework categories."""
        categories = set()
        for fw in self.frameworks.values():
            if not framework_type or fw.type == framework_type:
                categories.add(fw.category)
        return sorted(list(categories))

    def get_framework_types(self) -> List[str]:
        """Get list of available framework types."""
        return sorted(list(set(fw.type for fw in self.frameworks.values())))

# Example usage
if __name__ == "__main__":
    analyzer = FrameworkAnalyzer(
        framework_types=["css", "ui", "testing"],
        update_interval_hours=24,
        cache_enabled=True
    )
    
    # Example: Analyze text
    result = analyzer.process_text(
        "Building a website with Tailwind CSS and React, testing with Jest"
    )
    
    if result.success:
        print("\nAnalysis Results:")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"Analysis failed: {result.error}")

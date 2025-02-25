"""
Enhanced technology stack analyzer that dynamically discovers and validates
various technology components (languages, frameworks, libraries, tools, etc.).
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

from .utils import (
    BaseError, ValidationError, Cache, StateManager,
    OperationResult, monitor_performance
)

logger = logging.getLogger(__name__)

class TechAnalyzerError(BaseError):
    """Custom error for technology analysis operations."""
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
            recovery_hint or "Check technology configuration and sources"
        )

@dataclass
class TechInfo:
    """Enhanced data structure for technology information."""
    name: str
    type: str  # language, framework, library, tool, etc.
    category: str  # frontend, backend, database, testing, etc.
    description: str
    tags: List[str] = field(default_factory=list)
    github_url: Optional[str] = None
    package_manager: Optional[str] = None  # npm, pip, gem, etc.
    package_name: Optional[str] = None
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
    ecosystem: Dict[str, List[str]] = field(default_factory=dict)
    use_cases: List[str] = field(default_factory=list)
    learning_resources: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        data = asdict(self)
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechInfo':
        """Create from dictionary."""
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

class TechStackAnalyzer:
    """Enhanced analyzer that discovers and validates technology stack components."""

    def __init__(
        self,
        tech_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        update_interval_hours: int = 24,
        cache_enabled: bool = True,
        max_cache_size: int = 1000,
        log_level: int = logging.INFO,
        state_dir: Optional[Path] = None
    ):
        """Initialize the analyzer with enhanced configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Initialize configuration
        self.tech_types = tech_types or [
            "language", "framework", "library", "database",
            "tool", "service", "platform", "runtime"
        ]
        self.categories = categories or [
            "frontend", "backend", "database", "testing",
            "devops", "cloud", "mobile", "desktop"
        ]
        
        # Initialize state management
        state_dir = state_dir or Path("/tmp/tech_analyzer")
        self.state_manager = StateManager[Dict[str, Any]](
            state_dir / "tech_state.json"
        )
        
        # Initialize caches
        self.cache_enabled = cache_enabled
        self.results_cache = Cache[str, Dict[str, Any]](ttl=3600)
        self.tech_cache = Cache[str, TechInfo](ttl=3600)
        
        # Technology variations lookup
        self.variations = {
            # Languages
            'python': ['python', 'py', 'python3'],
            'javascript': ['javascript', 'js', 'node', 'nodejs'],
            'typescript': ['typescript', 'ts'],
            
            # Runtimes
            'nodejs': ['node.js', 'node', 'nodejs', 'node-js'],
            
            # Frontend Frameworks
            'react': ['react', 'reactjs', 'react.js'],
            'vue': ['vue', 'vuejs', 'vue.js'],
            'angular': ['angular', 'angularjs', 'angular.js'],
            
            # Backend Frameworks
            'django': ['django', 'djangoframework'],
            'express': ['express', 'expressjs', 'express.js'],
            'flask': ['flask', 'flaskframework'],
            
            # CSS Frameworks
            'tailwind': ['tailwind', 'tailwindcss', 'tailwind-css'],
            'bootstrap': ['bootstrap', 'bootstrapcss'],
            
            # Databases
            'postgresql': ['postgresql', 'postgres', 'psql'],
            'mongodb': ['mongodb', 'mongo'],
            
            # Testing
            'jest': ['jest', 'jestjs'],
            'pytest': ['pytest', 'py.test'],
            
            # DevOps
            'docker': ['docker', 'dockerfile'],
            'kubernetes': ['kubernetes', 'k8s'],
            
            # Cloud
            'aws': ['aws', 'amazon-web-services', 'amazon'],
            'gcp': ['gcp', 'google-cloud', 'google-cloud-platform']
        }
        
        # Build reverse lookup
        self.variation_lookup = {}
        for standard, variants in self.variations.items():
            for variant in variants:
                self.variation_lookup[variant] = standard
        
        # Initialize tech database
        self.technologies: Dict[str, TechInfo] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load state with validation."""
        result = self.state_manager.load_state()
        if result.success and result.data:
            self.technologies = {
                k: TechInfo.from_dict(v)
                for k, v in result.data.get("technologies", {}).items()
            }
            self.last_updated = datetime.fromisoformat(
                result.data.get("last_updated", "2000-01-01T00:00:00")
            )
        else:
            logger.warning("Failed to load state, initializing empty database")
            self.technologies = {}
            self.last_updated = datetime(2000, 1, 1)
            self._update_tech_database()

    def _save_state(self) -> None:
        """Save state atomically."""
        state = {
            "technologies": {
                k: v.to_dict() for k, v in self.technologies.items()
            },
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self.state_manager.save_state(state)

    @monitor_performance("Technology database update")
    def _update_tech_database(self) -> None:
        """Update technology database from all sources."""
        try:
            # Initialize with some default technologies
            self.technologies = {
                'python': TechInfo(
                    name='Python',
                    type='language',
                    category='backend',
                    description='A versatile programming language',
                    use_cases=['web', 'data-science', 'automation']
                ),
                'javascript': TechInfo(
                    name='JavaScript',
                    type='language',
                    category='frontend',
                    description='The language of the web',
                    use_cases=['web', 'mobile', 'desktop']
                ),
                'nodejs': TechInfo(
                    name='Node.js',
                    type='runtime',
                    category='backend',
                    description='JavaScript runtime built on Chrome\'s V8 JavaScript engine',
                    use_cases=['web', 'api', 'server']
                ),
                'react': TechInfo(
                    name='React',
                    type='framework',
                    category='frontend',
                    description='A JavaScript library for building user interfaces',
                    use_cases=['web', 'mobile']
                ),
                'django': TechInfo(
                    name='Django',
                    type='framework',
                    category='backend',
                    description='A high-level Python web framework',
                    use_cases=['web']
                ),
                'postgresql': TechInfo(
                    name='PostgreSQL',
                    type='database',
                    category='database',
                    description='A powerful, open source object-relational database',
                    use_cases=['web', 'enterprise']
                ),
                'mongodb': TechInfo(
                    name='MongoDB',
                    type='database',
                    category='database',
                    description='A NoSQL database',
                    use_cases=['web', 'mobile']
                ),
                'docker': TechInfo(
                    name='Docker',
                    type='tool',
                    category='devops',
                    description='A platform for developing, shipping, and running applications',
                    use_cases=['deployment', 'development']
                )
            }
            
            self._save_state()
            logger.info(f"Technology database updated with {len(self.technologies)} entries")
            
        except Exception as e:
            logger.error(f"Error updating technology database: {e}")
            raise TechAnalyzerError(
                f"Database update failed: {str(e)}",
                "DatabaseUpdateError",
                {"error": str(e)}
            )

    def _normalize_tech_name(self, name: str) -> str:
        """Normalize technology name for consistent matching."""
        name = name.strip('*').strip().lower()
        
        # Check variation lookup
        if name in self.variation_lookup:
            return self.variation_lookup[name]
            
        # Handle compound names
        for variation, standard in self.variation_lookup.items():
            if name.startswith(f"{variation}-") or name.endswith(f"-{variation}"):
                return standard
        
        return name

    @monitor_performance("Technology detection")
    def process_text(
        self,
        text: str,
        context: str = "",
        tech_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> OperationResult[Dict[str, Any]]:
        """Process text to identify technology stack components."""
        try:
            # Check cache
            cache_key = f"{text}:{context}:{tech_types}:{categories}"
            if self.cache_enabled and use_cache:
                cached = self.results_cache.get(cache_key)
                if cached:
                    return OperationResult(
                        success=True,
                        data=cached,
                        metadata={"cache_hit": True}
                    )
            
            # Initialize results
            results: Dict[str, Any] = {
                "identified_technologies": [],
                "tech_types": tech_types or self.tech_types,
                "categories": categories or self.categories,
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "stack_analysis": {
                    "completeness": {},
                    "compatibility": {},
                    "suggestions": []
                }
            }
            
            # Extract potential technology references
            text = text.lower()
            words = set(re.findall(
                r'\b(?:node\.?js|[a-z]+(?:[-.]?[a-z0-9]+)*(?:\.?js)?)\b',
                text
            ))
            
            # Process each word
            seen_techs: Set[str] = set()
            identified_techs: List[Dict[str, Any]] = []
            for word in words:
                normalized = self._normalize_tech_name(word)
                if normalized in self.technologies:
                    tech = self.technologies[normalized]
                    
                    # Apply filters
                    if tech_types and tech.type not in tech_types:
                        continue
                    if categories and tech.category not in categories:
                        continue
                        
                    if normalized not in seen_techs:
                        seen_techs.add(normalized)
                        identified_techs.append({
                            "name": tech.name,
                            "type": tech.type,
                            "category": tech.category,
                            "description": tech.description,
                            "confidence_score": self._calculate_confidence(word, normalized),
                            "popularity": tech.popularity_metrics,
                            "version_info": tech.version_info,
                            "ecosystem": tech.ecosystem,
                            "use_cases": tech.use_cases
                        })
            
            results["identified_technologies"] = identified_techs
            
            # Analyze stack completeness and compatibility
            if identified_techs:
                results["stack_analysis"] = self._analyze_stack(identified_techs)
            
            # Cache results
            if self.cache_enabled and use_cache:
                self.results_cache.set(cache_key, results)
            
            return OperationResult(
                success=True,
                data=results,
                metadata={
                    "cache_hit": False,
                    "tech_count": len(identified_techs)
                }
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=TechAnalyzerError(
                    f"Analysis failed: {str(e)}",
                    "AnalysisError",
                    {"text": text[:100], "error": str(e)}
                )
            )

    def _analyze_stack(
        self,
        technologies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze technology stack for completeness and compatibility."""
        analysis = {
            "completeness": {
                "frontend": False,
                "backend": False,
                "database": False,
                "testing": False
            },
            "compatibility": {
                "issues": [],
                "score": 1.0
            },
            "suggestions": []
        }
        
        # Check stack completeness
        tech_by_category: Dict[str, List[Dict[str, Any]]] = {}
        for tech in technologies:
            category = tech["category"]
            if category not in tech_by_category:
                tech_by_category[category] = []
            tech_by_category[category].append(tech)
            
        # Update completeness flags
        for category in analysis["completeness"]:
            analysis["completeness"][category] = category in tech_by_category
            
        # Check compatibility
        if len(technologies) > 1:
            for i, tech1 in enumerate(technologies):
                for tech2 in technologies[i+1:]:
                    compatibility = self._check_compatibility(tech1, tech2)
                    if compatibility["issues"]:
                        analysis["compatibility"]["issues"].extend(
                            compatibility["issues"]
                        )
                        analysis["compatibility"]["score"] *= compatibility["score"]
        
        # Generate suggestions
        if not analysis["completeness"]["frontend"]:
            analysis["suggestions"].append(
                "Consider adding a frontend framework (e.g., React, Vue)"
            )
        if not analysis["completeness"]["backend"]:
            analysis["suggestions"].append(
                "Consider adding a backend framework (e.g., Django, Express)"
            )
        if not analysis["completeness"]["database"]:
            analysis["suggestions"].append(
                "Consider adding a database (e.g., PostgreSQL, MongoDB)"
            )
        if not analysis["completeness"]["testing"]:
            analysis["suggestions"].append(
                "Consider adding testing tools (e.g., Jest, PyTest)"
            )
            
        return analysis

    def _check_compatibility(
        self,
        tech1: Dict[str, Any],
        tech2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compatibility between two technologies."""
        result = {
            "issues": [],
            "score": 1.0
        }
        
        # Check ecosystem compatibility
        ecosystem = tech1.get("ecosystem", {})
        requires = ecosystem.get("requires", [])
        if requires and tech2["name"] not in requires:
            result["issues"].append(
                f"{tech1['name']} may not be fully compatible with {tech2['name']}"
            )
            result["score"] = result["score"] * 0.8
            
        # Check version compatibility
        version_info = tech1.get("version_info", {})
        compatibility = version_info.get("compatibility", {})
        if compatibility and tech2["name"] in compatibility:
            compat_versions = compatibility[tech2["name"]]
            tech2_version = tech2.get("version_info", {}).get("latest")
            if tech2_version not in compat_versions:
                result["issues"].append(
                    f"Version compatibility issue between {tech1['name']} "
                    f"and {tech2['name']}"
                )
                result["score"] = result["score"] * 0.7
                
        return result

    def _calculate_confidence(self, original: str, normalized: str) -> float:
        """Calculate confidence score for technology detection."""
        base_score = 0.7
        
        # Exact match bonus
        if original.lower() == normalized:
            base_score += 0.3
            
        # Known variation bonus
        if original in self.variation_lookup:
            base_score += 0.2
            
        return min(base_score, 1.0)

    def get_tech_info(
        self,
        name: str,
        include_alternatives: bool = False,
        include_resources: bool = False
    ) -> OperationResult[TechInfo]:
        """Get detailed information about a technology."""
        try:
            normalized = self._normalize_tech_name(name)
            if normalized in self.technologies:
                tech = self.technologies[normalized]
                
                # Fetch alternatives if requested
                if include_alternatives:
                    tech.alternatives = self._find_alternatives(tech)
                    
                # Fetch learning resources if requested
                if include_resources:
                    tech.learning_resources = self._fetch_learning_resources(tech)
                    
                return OperationResult(
                    success=True,
                    data=tech
                )
                
            return OperationResult(
                success=False,
                error=TechAnalyzerError(
                    f"Technology not found: {name}",
                    "TechnologyNotFound"
                )
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=TechAnalyzerError(
                    f"Error fetching technology info: {str(e)}",
                    "InfoFetchError"
                )
            )

    def _find_alternatives(self, tech: TechInfo) -> List[str]:
        """Find alternative technologies of the same type and category."""
        alternatives = []
        for name, t in self.technologies.items():
            if (t.type == tech.type and
                t.category == tech.category and
                t.name != tech.name):
                alternatives.append(t.name)
        return alternatives

    def list_technologies(
        self,
        tech_type: Optional[str] = None,
        category: Optional[str] = None,
        validated_only: bool = False,
        min_stars: Optional[int] = None,
        include_resources: bool = False
    ) -> List[Dict[str, Any]]:
        """List technologies with filtering."""
        technologies = []
        for tech in self.technologies.values():
            if tech_type and tech.type != tech_type:
                continue
            if category and tech.category != category:
                continue
            if validated_only and not tech.is_validated:
                continue
            if min_stars and (not tech.stars or tech.stars < min_stars):
                continue
                
            tech_data = tech.to_dict()
            if include_resources:
                tech_data['learning_resources'] = self._fetch_learning_resources(tech)
            technologies.append(tech_data)
            
        return technologies

    def get_categories(self, tech_type: Optional[str] = None) -> List[str]:
        """Get list of technology categories."""
        categories = set()
        for tech in self.technologies.values():
            if not tech_type or tech.type == tech_type:
                categories.add(tech.category)
        return sorted(list(categories))

    def get_tech_types(self) -> List[str]:
        """Get list of available technology types."""
        return sorted(list(set(tech.type for tech in self.technologies.values())))

    def _fetch_learning_resources(self, tech: TechInfo) -> List[Dict[str, str]]:
        """Fetch learning resources for a technology."""
        resources = []
        
        # Official documentation
        if tech.documentation_url:
            resources.append({
                "type": "documentation",
                "title": f"Official {tech.name} Documentation",
                "url": tech.documentation_url
            })
            
        # GitHub repository
        if tech.github_url:
            resources.append({
                "type": "repository",
                "title": f"{tech.name} GitHub Repository",
                "url": tech.github_url
            })
            
        # Add more resource types as needed
        return resources

"""
CSS Framework analyzer system that dynamically manages framework keywords
and validates new entries against multiple sources.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import requests
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FrameworkInfo:
    """Data structure for CSS framework information."""
    name: str
    category: str
    description: str
    github_url: Optional[str] = None
    npm_package: Optional[str] = None
    stars: Optional[int] = None
    last_updated: Optional[datetime] = None
    validation_sources: List[str] = None
    discovery_context: Optional[str] = None
    is_validated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "github_url": self.github_url,
            "npm_package": self.npm_package,
            "stars": self.stars,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "validation_sources": self.validation_sources or [],
            "discovery_context": self.discovery_context,
            "is_validated": self.is_validated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameworkInfo':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            category=data["category"],
            description=data["description"],
            github_url=data.get("github_url"),
            npm_package=data.get("npm_package"),
            stars=data.get("stars"),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None,
            validation_sources=data.get("validation_sources", []),
            discovery_context=data.get("discovery_context"),
            is_validated=data.get("is_validated", False)
        )


class CSSFrameworkAnalyzer:
    """
    Analyzes and manages CSS framework keywords with dynamic updates
    and multi-source validation.
    """

    def __init__(self):
        """Initialize the analyzer with base dictionary and state management."""
        self.frameworks: Dict[str, FrameworkInfo] = {}
        self.state_file = Path(__file__).parent / "css_frameworks_state.json"
        self.lock = Lock()
        self.load_state()
        self._update_base_dictionary()

    def _update_base_dictionary(self) -> None:
        """Update base dictionary from awesome-css-frameworks."""
        try:
            url = "https://raw.githubusercontent.com/troxler/awesome-css-frameworks/master/readme.md"
            response = requests.get(url)
            response.raise_for_status()
            content = response.text

            # Parse markdown content
            current_category = "Uncategorized"
            for line in content.split('\n'):
                # Extract category
                if line.startswith('##'):
                    current_category = line.strip('# ').strip()
                    continue

                # Extract framework information
                if line.startswith('- ['):
                    try:
                        # Parse framework entry
                        name_match = re.match(r'\- \[(.*?)\]', line)
                        desc_match = re.search(r'\- \[.*?\].*? - (.*?)(?:\.|$)', line)
                        github_match = re.search(r'\((https://github\.com/[^)]+)\)', line)
                        
                        if name_match and desc_match:
                            name = name_match.group(1)
                            description = desc_match.group(1).strip()
                            github_url = github_match.group(1) if github_match else None

                            # Add to frameworks if not exists
                            if name.lower() not in self.frameworks:
                                self.frameworks[name.lower()] = FrameworkInfo(
                                    name=name,
                                    category=current_category,
                                    description=description,
                                    github_url=github_url,
                                    validation_sources=["awesome-css-frameworks"],
                                    is_validated=True,
                                    last_updated=datetime.now()
                                )

                    except Exception as e:
                        logger.warning(f"Error parsing framework entry: {e}")

            self.save_state()
            logger.info("Base dictionary updated successfully")

        except Exception as e:
            logger.error(f"Error updating base dictionary: {e}")

    def load_state(self) -> None:
        """Load state from file with error handling."""
        try:
            if self.state_file.exists():
                with self.lock:
                    data = json.loads(self.state_file.read_text())
                    self.frameworks = {
                        k.lower(): FrameworkInfo.from_dict(v)
                        for k, v in data.items()
                    }
                logger.info("State loaded successfully")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            self.frameworks = {}

    def save_state(self) -> None:
        """Save state to file atomically."""
        with self.lock:
            temp_file = self.state_file.with_suffix('.tmp')
            try:
                # Save to temporary file
                data = {
                    k: v.to_dict()
                    for k, v in self.frameworks.items()
                }
                temp_file.write_text(json.dumps(data, indent=2))
                
                # Rename to actual file
                temp_file.rename(self.state_file)
                logger.info("State saved successfully")
                
            except Exception as e:
                logger.error(f"Error saving state: {e}")
                if temp_file.exists():
                    temp_file.unlink()

    async def validate_framework(self, name: str, github_url: Optional[str] = None) -> bool:
        """
        Validate a framework through multiple sources.
        
        Args:
            name: Framework name
            github_url: Optional GitHub URL
            
        Returns:
            bool: Whether validation was successful
        """
        validation_sources = []
        
        try:
            # Check npm registry
            npm_url = f"https://registry.npmjs.org/{name}"
            response = requests.get(npm_url)
            if response.status_code == 200:
                validation_sources.append("npm")
                data = response.json()
                if "description" in data:
                    self.frameworks[name.lower()].description = data["description"]
                if "homepage" in data:
                    self.frameworks[name.lower()].github_url = data["homepage"]

            # Check GitHub if URL provided
            if github_url:
                if github_url.startswith("https://github.com/"):
                    repo_path = github_url.replace("https://github.com/", "")
                    api_url = f"https://api.github.com/repos/{repo_path}"
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        validation_sources.append("github")
                        data = response.json()
                        self.frameworks[name.lower()].stars = data.get("stargazers_count")
                        self.frameworks[name.lower()].last_updated = datetime.strptime(
                            data.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ"
                        )

            # Update validation status
            if validation_sources:
                self.frameworks[name.lower()].validation_sources = validation_sources
                self.frameworks[name.lower()].is_validated = True
                self.save_state()
                return True

        except Exception as e:
            logger.error(f"Error validating framework {name}: {e}")

        return False

    def process_text(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Process text to identify and validate CSS framework references.
        
        Args:
            text: Input text to analyze
            context: Optional context about where the text came from
            
        Returns:
            Dict containing analysis results
        """
        results = {
            "identified_frameworks": [],
            "new_frameworks": [],
            "requires_agent": False,
            "timestamp": datetime.now().isoformat()
        }

        # Extract potential framework references
        words = re.findall(r'\b\w+(?:-\w+)*\b', text.lower())
        
        for word in words:
            # Check if it's a known framework
            if word in self.frameworks:
                framework = self.frameworks[word]
                results["identified_frameworks"].append({
                    "name": framework.name,
                    "is_validated": framework.is_validated,
                    "category": framework.category
                })
                
                # Check if agent creation is warranted
                agent_triggers = [
                    "using", "with", "implement", "create", "build",
                    "develop", "integrate", "setup", "configure"
                ]
                if any(trigger in text.lower() for trigger in agent_triggers):
                    results["requires_agent"] = True
                
            # Check if it might be a new framework
            elif re.search(r'(?:css|framework|style|ui kit)', text.lower()):
                # Add as unvalidated framework
                self.frameworks[word] = FrameworkInfo(
                    name=word,
                    category="Pending Validation",
                    description=f"Discovered in context: {context}",
                    discovery_context=context,
                    validation_sources=[],
                    is_validated=False,
                    last_updated=datetime.now()
                )
                
                results["new_frameworks"].append({
                    "name": word,
                    "requires_validation": True
                })
                
                self.save_state()

        return results

    def get_framework_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a framework."""
        name_lower = name.lower()
        if name_lower in self.frameworks:
            return self.frameworks[name_lower].to_dict()
        return None

    def list_frameworks(
        self,
        category: Optional[str] = None,
        validated_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List frameworks with optional filtering.
        
        Args:
            category: Optional category filter
            validated_only: Whether to only return validated frameworks
            
        Returns:
            List of framework information
        """
        frameworks = []
        for framework in self.frameworks.values():
            if validated_only and not framework.is_validated:
                continue
            if category and framework.category != category:
                continue
            frameworks.append(framework.to_dict())
        return frameworks

    def get_categories(self) -> List[str]:
        """Get list of all framework categories."""
        return sorted(list(set(
            f.category for f in self.frameworks.values()
        )))

    def search_frameworks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search frameworks by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching frameworks
        """
        query_lower = query.lower()
        return [
            f.to_dict() for f in self.frameworks.values()
            if query_lower in f.name.lower() or
               query_lower in f.description.lower()
        ]


# Example usage
if __name__ == "__main__":
    analyzer = CSSFrameworkAnalyzer()
    
    # Example text analysis
    text = "I want to create a website using Tailwind CSS and maybe try Bootstrap"
    results = analyzer.process_text(text, "Example usage")
    
    print("\nAnalysis Results:")
    print(json.dumps(results, indent=2))
    
    print("\nFramework Categories:")
    print(analyzer.get_categories())
    
    print("\nValidated Frameworks:")
    print(json.dumps(analyzer.list_frameworks(validated_only=True), indent=2))

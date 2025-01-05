"""
Enhanced CSS Framework analyzer system that dynamically discovers and validates
CSS frameworks from multiple authoritative sources.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import requests
from threading import Lock
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FrameworkInfo:
    """Enhanced data structure for CSS framework information."""
    name: str
    category: str
    description: str
    tags: List[str] = field(default_factory=lambda: ["CSS Frameworks"])
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


class CSSFrameworkAnalyzer:
    """
    Enhanced analyzer that discovers and validates CSS frameworks from
    multiple authoritative sources.
    """

    def __init__(self, update_interval_hours: int = 24):
        """
        Initialize the analyzer with enhanced source checking.
        
        Args:
            update_interval_hours: Hours between framework database updates
        """
        # Framework variations lookup
        self.framework_variations = {
            'tailwind': ['tailwind', 'tailwindcss', 'tailwind-css', 'tailwind css'],
            'bootstrap': ['bootstrap', 'bootstrapui', 'bootstrap-ui', 'bootstrap ui', 'bootstrap css'],
            'bulma': ['bulma', 'bulmacss', 'bulma-css', 'bulma css'],
            'foundation': ['foundation', 'foundationcss', 'foundation-css', 'foundation css'],
            'materialize': ['materialize', 'materializecss', 'materialize-css', 'materialize css'],
            'semantic': [
                'semantic', 'semanticui', 'semantic-ui', 'semantic ui',
                'semantic-ui css', 'semanticui css', 'semantic ui css',
                'semantic framework', 'semantic ui framework', 'semantic-ui framework',
                'semantic-ui-css', 'semantic ui css framework', 'semantic-ui css framework',
                'semantic ui framework', 'semantic-ui framework', 'semantic framework'
            ],
            'pure': ['pure', 'purecss', 'pure-css', 'pure css'],
            'uikit': ['uikit', 'ui-kit', 'ui kit'],
            'tachyons': ['tachyons', 'tachyonscss', 'tachyons css'],
            'skeleton': ['skeleton', 'skeletoncss', 'skeleton css'],
            'milligram': ['milligram', 'milligramcss', 'milligram css'],
            'fomantic': [
                'fomantic', 'fomantic-ui', 'fomantic ui',
                'fomantic ui css', 'fomantic-ui css',
                'fomantic framework', 'fomantic ui framework',
                'fomantic-ui framework', 'fomantic ui css framework'
            ]
        }
        
        # Build reverse lookup for variations
        self.variation_lookup = {}
        for standard, variations in self.framework_variations.items():
            for variation in variations:
                self.variation_lookup[variation] = standard
        
        self.frameworks: Dict[str, FrameworkInfo] = {}
        self.state_file = Path(__file__).parent / "css_frameworks_state.json"
        self.lock = Lock()
        self.update_interval_hours = update_interval_hours
        self.load_state()
        
        # Only update if state is empty or outdated
        if (not self.frameworks or 
            not hasattr(self, 'last_updated') or
            (datetime.now() - self.last_updated).total_seconds() > update_interval_hours * 3600):
            self._update_framework_database()

    def _fetch_github_awesome_list(self) -> List[Dict[str, Any]]:
        """Fetch and parse the awesome-css-frameworks list."""
        try:
            url = "https://raw.githubusercontent.com/troxler/awesome-css-frameworks/master/readme.md"
            response = requests.get(url)
            response.raise_for_status()
            content = response.text

            frameworks = []
            current_category = "General"
            
            for line in content.split('\n'):
                if line.startswith('##'):
                    current_category = line.strip('# ').strip()
                elif line.startswith('- ['):
                    try:
                        name_match = re.match(r'\- \[(.*?)\]', line)
                        desc_match = re.search(r'\- \[.*?\].*? - (.*?)(?:\.|$)', line)
                        github_match = re.search(r'\((https://github\.com/[^)]+)\)', line)
                        
                        if name_match and desc_match:
                            frameworks.append({
                                "name": name_match.group(1),
                                "category": current_category,
                                "description": desc_match.group(1).strip(),
                                "github_url": github_match.group(1) if github_match else None,
                                "source": "awesome-css-frameworks"
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing framework entry: {e}")

            return frameworks

        except Exception as e:
            logger.error(f"Error fetching awesome-css-frameworks: {e}")
            return []

    def _fetch_wikipedia_frameworks(self) -> List[Dict[str, Any]]:
        """Fetch CSS frameworks listed on Wikipedia."""
        try:
            url = "https://en.wikipedia.org/wiki/CSS_framework"
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            frameworks = []
            
            # Find framework lists in the article
            for ul in soup.find_all('ul'):
                for li in ul.find_all('li'):
                    if li.find('a'):
                        name = li.find('a').text
                        desc = li.text.replace(name, '').strip(' -:')
                        if name and desc:
                            frameworks.append({
                                "name": name,
                                "category": "Wikipedia Listed",
                                "description": desc,
                                "source": "wikipedia"
                            })

            return frameworks

        except Exception as e:
            logger.error(f"Error fetching Wikipedia frameworks: {e}")
            return []

    def _fetch_npm_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch framework information from npm."""
        try:
            response = requests.get(f"https://registry.npmjs.org/{name}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "npm_package": name,
                    "description": data.get("description", ""),
                    "latest_version": data.get("dist-tags", {}).get("latest"),
                    "maintainers": [m.get("name") for m in data.get("maintainers", [])],
                    "homepage": data.get("homepage")
                }
        except Exception as e:
            logger.debug(f"Error fetching npm info for {name}: {e}")
        return None

    def _fetch_github_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch framework information from GitHub."""
        try:
            if url.startswith("https://github.com/"):
                repo_path = url.replace("https://github.com/", "")
                api_url = f"https://api.github.com/repos/{repo_path}"
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "stars": data.get("stargazers_count"),
                        "last_updated": datetime.strptime(
                            data.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "open_issues": data.get("open_issues_count"),
                        "forks": data.get("forks_count"),
                        "description": data.get("description")
                    }
        except Exception as e:
            logger.debug(f"Error fetching GitHub info for {url}: {e}")
        return None

    def _update_framework_database(self) -> None:
        """Update framework database from all sources."""
        try:
            # Fetch from all sources
            github_frameworks = self._fetch_github_awesome_list()
            wiki_frameworks = self._fetch_wikipedia_frameworks()
            
            # Combine frameworks from all sources
            all_frameworks = github_frameworks + wiki_frameworks
            
            # Process each framework
            for framework_data in all_frameworks:
                # Clean up and normalize framework name
                name = framework_data["name"].strip('*').strip()
                display_name = name  # Keep original casing for display
                
                # Special case for Semantic UI
                if name.lower() in ['semantic ui', 'semantic-ui', 'semanticui']:
                    name_lower = 'semantic'
                else:
                    name_lower = self._normalize_framework_name(name)
                
                if name_lower not in self.frameworks:
                    # Create new framework entry
                    framework = FrameworkInfo(
                        name=display_name if not name.lower().startswith('semantic') else 'Semantic UI',
                        category=framework_data["category"],
                        description=framework_data["description"],
                        github_url=framework_data.get("github_url"),
                        validation_sources=[framework_data["source"]],
                        is_validated=True,
                        last_updated=datetime.now()
                    )
                    
                    # Fetch additional information
                    if framework.github_url:
                        github_info = self._fetch_github_info(framework.github_url)
                        if github_info:
                            framework.stars = github_info["stars"]
                            framework.last_updated = github_info["last_updated"]
                            framework.popularity_metrics.update({
                                "github_stars": github_info["stars"],
                                "open_issues": github_info["open_issues"],
                                "forks": github_info["forks"]
                            })
                    
                    # Try to find npm package
                    npm_info = self._fetch_npm_info(name_lower)
                    if npm_info:
                        framework.npm_package = npm_info["npm_package"]
                        framework.documentation_url = npm_info["homepage"]
                        framework.popularity_metrics["npm_package"] = npm_info["latest_version"]
                    
                    self.frameworks[name_lower] = framework
                else:
                    # Update existing framework
                    framework = self.frameworks[name_lower]
                    if framework_data["source"] not in framework.validation_sources:
                        framework.validation_sources.append(framework_data["source"])
                        framework.last_updated = datetime.now()

            self.save_state()
            logger.info(f"Framework database updated with {len(self.frameworks)} frameworks")

        except Exception as e:
            logger.error(f"Error updating framework database: {e}")

    def load_state(self) -> None:
        """Load state from file with error handling."""
        try:
            if self.state_file.exists():
                with self.lock:
                    data = json.loads(self.state_file.read_text())
                    frameworks_data = {}
                    for k, v in data.get('frameworks', {}).items():
                        # Special case for Semantic UI
                        if k.lower() in ['semantic ui', 'semantic-ui', 'semanticui']:
                            frameworks_data['semantic'] = FrameworkInfo.from_dict(v)
                        else:
                            frameworks_data[k.lower()] = FrameworkInfo.from_dict(v)
                    self.frameworks = frameworks_data
                    self.last_updated = datetime.fromisoformat(data.get('last_updated', '2000-01-01T00:00:00'))
                logger.info("State loaded successfully")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            self.frameworks = {}
            self.last_updated = datetime(2000, 1, 1)  # Force update

    def save_state(self) -> None:
        """Save state to file atomically."""
        with self.lock:
            temp_file = self.state_file.with_suffix('.tmp')
            try:
                data = {
                    'frameworks': {
                        k: v.to_dict()
                        for k, v in self.frameworks.items()
                    },
                    'last_updated': datetime.now().isoformat()
                }
                temp_file.write_text(json.dumps(data, indent=2))
                temp_file.rename(self.state_file)
                self.last_updated = datetime.now()
                logger.info("State saved successfully")
            except Exception as e:
                logger.error(f"Error saving state: {e}")
                if temp_file.exists():
                    temp_file.unlink()

    def _normalize_framework_name(self, name: str) -> str:
        """
        Normalize framework name for consistent matching.
        
        This function handles various forms of framework names:
        - Different casings (Tailwind, TAILWIND, tailwind)
        - Common variations (tailwind css, tailwindcss, tailwind-css)
        - Special characters (*, -, _, spaces)
        """
        # Remove asterisks and extra whitespace
        name = name.strip('*').strip()
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove common suffixes and variations
        suffixes = [
            ' css', ' framework', ' ui', ' system', ' kit',
            '-css', '-framework', '-ui', '-system', '-kit',
            '.css', '.js', '.min', '.dev'
        ]
        
        # Try each suffix
        original_name = name
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        # Remove special characters and normalize spaces
        name = re.sub(r'[^a-z0-9\s-]+', '', name).strip()
        name = re.sub(r'[-\s]+', ' ', name)
        
        # Check if it's a known variation
        if name in self.variation_lookup:
            return self.variation_lookup[name]
            
        # Try without spaces
        name_no_spaces = name.replace(' ', '')
        if name_no_spaces in self.variation_lookup:
            return self.variation_lookup[name_no_spaces]
        
        return name

    def process_text(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Process text to identify CSS framework references with enhanced detection.
        
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
        # Convert text to lowercase for matching
        text = text.lower()
        
        # Look for framework references with different patterns
        patterns = [
            # Framework-specific patterns first (more specific)
            r'\b(?:semantic[-\s]*ui|fomantic[-\s]*ui)(?:[-\s]*(?:css|framework))?\b',
            r'\b(?:tailwind|bootstrap|bulma|foundation)(?:[-\s]*(?:css|ui|framework))?\b',
            # Multi-word with optional suffix: "semantic ui css"
            r'\b\w+(?:[-\s]+\w+)+(?:[-\s]+(?:css|framework|ui))?\b',
            # Single word with optional suffix: "bootstrap css"
            r'\b\w+(?:[-\s]+(?:css|framework|ui))?\b',
            # Compound names with framework
            r'\b\w+(?:[-\s]+\w+)*[-\s]+framework\b',
            # UI-specific patterns
            r'\b\w+(?:[-\s]+ui|[-\s]+framework)\b',
            # Framework-specific compound patterns
            r'\b(?:semantic[-\s]*ui[-\s]*(?:css|framework))\b',
            r'\b(?:semantic[-\s]*(?:css|framework))\b'
        ]
        
        # Get all potential matches
        words = set()  # Use set to avoid duplicates
        for pattern in patterns:
            matches = re.findall(pattern, text)
            words.update(matches)
        
        # Check if agent creation is warranted
        agent_triggers = [
            "using", "with", "implement", "create", "build",
            "develop", "integrate", "setup", "configure"
        ]
        requires_agent = any(trigger in text.lower() for trigger in agent_triggers)
        
        # Process each word
        seen_frameworks = set()  # Track unique frameworks
        for word in words:
            # Try different variations of the word
            variations = [
                word,  # Original form
                word.replace('-', ' '),  # Replace hyphens with spaces
                word.replace(' ', ''),  # Remove spaces
                re.sub(r'[-\s]+(?:css|framework|ui)$', '', word),  # Remove suffixes
                # Handle multi-word variations
                word.replace('-', ' ').replace('ui', 'ui css'),
                word.replace('-', ' ').replace('ui', 'ui framework'),
                # Special cases for UI frameworks
                re.sub(r'(ui)$', r'\1 css', word),
                re.sub(r'(ui)$', r'\1 framework', word),
                # Handle framework suffix
                f"{word} framework",
                word.replace('framework', '').strip(),
                # Handle compound names
                re.sub(r'[-\s]+', '', word),  # Remove all separators
                re.sub(r'[-\s]+', ' ', word)  # Normalize separators to spaces
            ]
            
            # Check each variation
            for variation in variations:
                normalized = self._normalize_framework_name(variation)
                if normalized in self.frameworks and normalized not in seen_frameworks:
                    framework = self.frameworks[normalized]
                    seen_frameworks.add(normalized)
                    results["identified_frameworks"].append({
                        "name": framework.name,
                        "is_validated": framework.is_validated,
                        "category": framework.category,
                        "tags": framework.tags,
                        "popularity": framework.popularity_metrics
                    })
                    
                    if requires_agent:
                        results["requires_agent"] = True

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
        validated_only: bool = False,
        min_stars: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List frameworks with enhanced filtering.
        
        Args:
            category: Optional category filter
            validated_only: Whether to only return validated frameworks
            min_stars: Minimum number of GitHub stars
            
        Returns:
            List of framework information
        """
        frameworks = []
        for framework in self.frameworks.values():
            if validated_only and not framework.is_validated:
                continue
            if category and framework.category != category:
                continue
            if min_stars and (not framework.stars or framework.stars < min_stars):
                continue
            frameworks.append(framework.to_dict())
        return frameworks

    def get_categories(self) -> List[str]:
        """Get list of all framework categories."""
        return sorted(list(set(
            f.category for f in self.frameworks.values()
        )))

    def search_frameworks(
        self,
        query: str,
        include_unvalidated: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Enhanced framework search.
        
        Args:
            query: Search query
            include_unvalidated: Whether to include unvalidated frameworks
            
        Returns:
            List of matching frameworks
        """
        query_lower = query.lower()
        results = []
        
        for framework in self.frameworks.values():
            if not include_unvalidated and not framework.is_validated:
                continue
                
            # Check various fields for matches
            if (query_lower in framework.name.lower() or
                query_lower in framework.description.lower() or
                any(query_lower in tag.lower() for tag in framework.tags) or
                query_lower in framework.category.lower()):
                results.append(framework.to_dict())
                
        return results


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
    frameworks = analyzer.list_frameworks(validated_only=True)
    print(f"Found {len(frameworks)} validated frameworks")
    for framework in frameworks:
        print(f"\n{framework['name']}:")
        print(f"  Category: {framework['category']}")
        print(f"  Stars: {framework.get('stars', 'N/A')}")
        print(f"  Tags: {', '.join(framework['tags'])}")

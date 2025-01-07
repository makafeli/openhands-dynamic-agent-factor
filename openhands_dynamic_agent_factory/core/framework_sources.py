"""
Framework data sources and fetching utilities.
Provides methods to fetch framework information from various authoritative sources.
"""

import re
import logging
from typing import Dict, List, Any, Optional, cast
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from .utils import monitor_performance, OperationResult, BaseError

logger = logging.getLogger(__name__)

class FrameworkSourceError(BaseError):
    """Error when fetching framework data."""
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
            recovery_hint or "Check network connection and source availability"
        )

@monitor_performance("CSS framework fetch")
def fetch_css_frameworks() -> List[Dict[str, Any]]:
    """Fetch CSS framework information from multiple sources."""
    frameworks: List[Dict[str, Any]] = []
    
    try:
        # Fetch from awesome-css-frameworks
        url = "https://raw.githubusercontent.com/troxler/awesome-css-frameworks/master/readme.md"
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        
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
                            "type": "css",
                            "category": current_category,
                            "description": desc_match.group(1).strip(),
                            "github_url": github_match.group(1) if github_match else None,
                            "source": "awesome-css-frameworks"
                        })
                except Exception as e:
                    logger.warning(f"Error parsing CSS framework entry: {e}")
                    
    except Exception as e:
        logger.error(f"Error fetching CSS frameworks: {e}")
        
    return frameworks

@monitor_performance("UI framework fetch")
def fetch_ui_frameworks() -> List[Dict[str, Any]]:
    """Fetch UI framework information from multiple sources."""
    frameworks: List[Dict[str, Any]] = []
    
    try:
        # Fetch from awesome-javascript
        url = "https://raw.githubusercontent.com/sorrycc/awesome-javascript/master/README.md"
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        
        current_category = "General"
        for line in content.split('\n'):
            if line.startswith('##'):
                current_category = line.strip('# ').strip()
            elif 'framework' in line.lower() and line.startswith('- ['):
                try:
                    name_match = re.match(r'\- \[(.*?)\]', line)
                    desc_match = re.search(r'\- \[.*?\].*? - (.*?)(?:\.|$)', line)
                    github_match = re.search(r'\((https://github\.com/[^)]+)\)', line)
                    
                    if name_match and desc_match:
                        frameworks.append({
                            "name": name_match.group(1),
                            "type": "ui",
                            "category": current_category,
                            "description": desc_match.group(1).strip(),
                            "github_url": github_match.group(1) if github_match else None,
                            "source": "awesome-javascript"
                        })
                except Exception as e:
                    logger.warning(f"Error parsing UI framework entry: {e}")
                    
    except Exception as e:
        logger.error(f"Error fetching UI frameworks: {e}")
        
    return frameworks

@monitor_performance("Testing framework fetch")
def fetch_testing_frameworks() -> List[Dict[str, Any]]:
    """Fetch testing framework information from multiple sources."""
    frameworks: List[Dict[str, Any]] = []
    
    try:
        # Fetch from awesome-testing
        url = "https://raw.githubusercontent.com/TheJambo/awesome-testing/master/README.md"
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        
        current_category = "General"
        for line in content.split('\n'):
            if line.startswith('##'):
                current_category = line.strip('# ').strip()
            elif ('test' in line.lower() or 'framework' in line.lower()) and line.startswith('- ['):
                try:
                    name_match = re.match(r'\- \[(.*?)\]', line)
                    desc_match = re.search(r'\- \[.*?\].*? - (.*?)(?:\.|$)', line)
                    github_match = re.search(r'\((https://github\.com/[^)]+)\)', line)
                    
                    if name_match and desc_match:
                        frameworks.append({
                            "name": name_match.group(1),
                            "type": "testing",
                            "category": current_category,
                            "description": desc_match.group(1).strip(),
                            "github_url": github_match.group(1) if github_match else None,
                            "source": "awesome-testing"
                        })
                except Exception as e:
                    logger.warning(f"Error parsing testing framework entry: {e}")
                    
    except Exception as e:
        logger.error(f"Error fetching testing frameworks: {e}")
        
    return frameworks

@monitor_performance("GitHub info fetch")
def fetch_github_info(url: str) -> Optional[Dict[str, Any]]:
    """Fetch framework information from GitHub."""
    try:
        if url.startswith("https://github.com/"):
            repo_path = url.replace("https://github.com/", "")
            api_url = f"https://api.github.com/repos/{repo_path}"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return cast(Dict[str, Any], {
                    "stars": data.get("stargazers_count"),
                    "last_updated": datetime.strptime(
                        data.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "open_issues": data.get("open_issues_count"),
                    "forks": data.get("forks_count"),
                    "description": data.get("description")
                })
    except Exception as e:
        logger.debug(f"Error fetching GitHub info for {url}: {e}")
    return None

@monitor_performance("NPM info fetch")
def fetch_npm_info(name: str) -> Optional[Dict[str, Any]]:
    """Fetch framework information from npm."""
    try:
        response = requests.get(f"https://registry.npmjs.org/{name}")
        if response.status_code == 200:
            data = response.json()
            return cast(Dict[str, Any], {
                "npm_package": name,
                "description": data.get("description", ""),
                "latest_version": data.get("dist-tags", {}).get("latest"),
                "versions": list(data.get("versions", {}).keys()),
                "maintainers": [m.get("name") for m in data.get("maintainers", [])],
                "homepage": data.get("homepage")
            })
    except Exception as e:
        logger.debug(f"Error fetching npm info for {name}: {e}")
    return None

"""
CI/CD integration for CSS Framework Analyzer.
Provides automated analysis in GitHub Actions and GitLab CI pipelines.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import re

from .css_framework_analyzer import CSSFrameworkAnalyzer
from .templates import TemplateManager

# Configure logging
logger = logging.getLogger(__name__)

class CIAnalyzer:
    """Framework analyzer for CI environments."""

    def __init__(
        self,
        repo_path: Optional[str] = None,
        template: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """Initialize CI analyzer."""
        self.repo_path = Path(repo_path or os.getcwd())
        self.analyzer = CSSFrameworkAnalyzer()
        self.template_manager = TemplateManager()
        self.template = template
        self.config = self._load_config(config_path) if config_path else {}
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load CI configuration."""
        try:
            with open(path) as f:
                config = json.load(f)
            return self._validate_config(config)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
            
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CI configuration."""
        valid_config = {
            'include_patterns': config.get('include_patterns', ['**/*.{html,css,js,jsx,ts,tsx}']),
            'exclude_patterns': config.get('exclude_patterns', ['**/node_modules/**', '**/vendor/**']),
            'min_confidence': float(config.get('min_confidence', 0.7)),
            'fail_on_detection': bool(config.get('fail_on_detection', False)),
            'comment_on_pr': bool(config.get('comment_on_pr', True)),
            'create_report': bool(config.get('create_report', True)),
            'report_path': config.get('report_path', 'framework-analysis.json')
        }
        return valid_config

    def analyze_repository(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Analyze entire repository."""
        results = []
        warnings = []
        
        # Find files to analyze
        files = self._find_files()
        if not files:
            warnings.append("No files found matching include patterns")
            return results, warnings
            
        # Analyze each file
        for file_path in files:
            try:
                file_results = self._analyze_file(file_path)
                if file_results:
                    results.append({
                        'file': str(file_path.relative_to(self.repo_path)),
                        'frameworks': file_results
                    })
            except Exception as e:
                warnings.append(f"Failed to analyze {file_path}: {e}")
                
        return results, warnings

    def _find_files(self) -> List[Path]:
        """Find files to analyze based on patterns."""
        from glob import glob
        
        files = set()
        for pattern in self.config.get('include_patterns', []):
            matches = glob(str(self.repo_path / pattern), recursive=True)
            files.update(Path(p) for p in matches)
            
        # Apply exclude patterns
        for pattern in self.config.get('exclude_patterns', []):
            excludes = set(Path(p) for p in glob(str(self.repo_path / pattern), recursive=True))
            files -= excludes
            
        return sorted(files)

    def _analyze_file(self, path: Path) -> List[Dict[str, Any]]:
        """Analyze single file."""
        try:
            content = path.read_text()
            results = self.analyzer.process_text(
                content,
                template=self.template
            )
            
            frameworks = []
            for fw in results.get('identified_frameworks', []):
                if fw.get('confidence_score', 0) >= self.config.get('min_confidence', 0.7):
                    frameworks.append(fw)
                    
            return frameworks
            
        except Exception as e:
            logger.error(f"Error analyzing {path}: {e}")
            return []

    def create_report(self, results: List[Dict[str, Any]], warnings: List[str]) -> None:
        """Create analysis report."""
        if not self.config.get('create_report', True):
            return
            
        report = {
            'timestamp': datetime.now().isoformat(),
            'repository': str(self.repo_path),
            'results': results,
            'warnings': warnings,
            'summary': self._create_summary(results)
        }
        
        report_path = Path(self.config.get('report_path', 'framework-analysis.json'))
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Analysis report saved to {report_path}")

    def _create_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create analysis summary."""
        framework_counts = {}
        file_count = len(results)
        framework_files = {}
        
        for result in results:
            for fw in result.get('frameworks', []):
                name = fw['name']
                framework_counts[name] = framework_counts.get(name, 0) + 1
                if name not in framework_files:
                    framework_files[name] = []
                framework_files[name].append(result['file'])
                
        return {
            'total_files': file_count,
            'framework_counts': framework_counts,
            'framework_files': framework_files
        }

    def create_pr_comment(self, results: List[Dict[str, Any]], warnings: List[str]) -> str:
        """Create pull request comment."""
        summary = self._create_summary(results)
        
        comment = "## CSS Framework Analysis\n\n"
        
        if not results:
            comment += "No frameworks detected in changed files.\n"
            return comment
            
        # Framework summary
        comment += "### Detected Frameworks\n\n"
        for fw, count in summary['framework_counts'].items():
            comment += f"- **{fw}**: Found in {count} files\n"
        
        # File details
        comment += "\n### File Details\n\n"
        for fw, files in summary['framework_files'].items():
            comment += f"\n#### {fw}\n"
            for file in files[:5]:  # Limit to 5 files per framework
                comment += f"- `{file}`\n"
            if len(files) > 5:
                comment += f"- ... and {len(files) - 5} more files\n"
                
        # Warnings
        if warnings:
            comment += "\n### Warnings\n\n"
            for warning in warnings:
                comment += f"- {warning}\n"
                
        return comment

def create_github_action() -> None:
    """Create GitHub Action workflow file."""
    workflow = """name: CSS Framework Analysis

on:
  pull_request:
    paths:
      - '**/*.html'
      - '**/*.css'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.ts'
      - '**/*.tsx'
  push:
    branches: [ main, master ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install openhands-dynamic-agent-factor
          
      - name: Analyze frameworks
        run: |
          python -m openhands_dynamic_agent_factory.core.ci_integration analyze
          
      - name: Upload analysis report
        uses: actions/upload-artifact@v2
        with:
          name: framework-analysis
          path: framework-analysis.json
          
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v5
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('framework-analysis.json', 'utf8'));
            const analyzer = require('./openhands_dynamic_agent_factory/core/ci_integration.py');
            const comment = analyzer.create_pr_comment(report.results, report.warnings);
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
"""
    
    path = Path('.github/workflows/framework-analysis.yml')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(workflow)
    logger.info(f"Created GitHub Action workflow: {path}")

def create_gitlab_ci() -> None:
    """Create GitLab CI configuration file."""
    config = """framework-analysis:
  image: python:3
  script:
    - pip install openhands-dynamic-agent-factor
    - python -m openhands_dynamic_agent_factory.core.ci_integration analyze
  artifacts:
    reports:
      json: framework-analysis.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - "**/*.html"
        - "**/*.css"
        - "**/*.js"
        - "**/*.jsx"
        - "**/*.ts"
        - "**/*.tsx"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""
    
    path = Path('.gitlab-ci.yml')
    path.write_text(config)
    logger.info(f"Created GitLab CI configuration: {path}")

def main():
    """CLI entry point for CI integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CSS Framework Analyzer CI Integration")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze repository')
    analyze_parser.add_argument('--repo', help='Repository path')
    analyze_parser.add_argument('--template', help='Analysis template')
    analyze_parser.add_argument('--config', help='Configuration file')
    
    # Setup commands
    setup_parser = subparsers.add_parser('setup', help='Setup CI integration')
    setup_parser.add_argument('--type', choices=['github', 'gitlab'], required=True,
                            help='CI platform type')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'analyze':
            analyzer = CIAnalyzer(
                repo_path=args.repo,
                template=args.template,
                config_path=args.config
            )
            
            results, warnings = analyzer.analyze_repository()
            analyzer.create_report(results, warnings)
            
            # Exit with error if configured
            if (analyzer.config.get('fail_on_detection', False) and
                any(len(r.get('frameworks', [])) > 0 for r in results)):
                sys.exit(1)
                
        elif args.command == 'setup':
            if args.type == 'github':
                create_github_action()
            else:
                create_gitlab_ci()
                
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

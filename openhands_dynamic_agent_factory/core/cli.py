#!/usr/bin/env python3
"""
Command-line interface for the CSS Framework Analyzer.
Provides interactive analysis and visualization of CSS framework detection.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import webbrowser
from datetime import datetime

from .css_framework_analyzer import CSSFrameworkAnalyzer
from .templates import AnalysisTemplate, load_template, save_template

class FrameworkAnalyzerCLI:
    """Interactive CLI for CSS Framework Analysis."""

    def __init__(self):
        self.analyzer = CSSFrameworkAnalyzer(
            cache_enabled=True,
            max_cache_size=1000,
            log_level=logging.INFO
        )
        self.current_results: Dict[str, Any] = {}
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def analyze_text(self, text: str, template: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text using optional template."""
        if template:
            template_path = self.templates_dir / f"{template}.json"
            if template_path.exists():
                template_config = load_template(template_path)
                return self.analyzer.process_text(
                    text,
                    use_cache=template_config.get('use_cache', True),
                    fallback_enabled=template_config.get('fallback_enabled', True)
                )
        
        return self.analyzer.process_text(text)

    def save_results(self, results: Dict[str, Any], output: Optional[str] = None) -> None:
        """Save analysis results to file."""
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            results['saved_at'] = datetime.now().isoformat()
            results['cli_version'] = '1.0.0'
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")

    def create_template(self, name: str, config: Dict[str, Any]) -> None:
        """Create new analysis template."""
        template = AnalysisTemplate(
            name=name,
            description=config.get('description', ''),
            use_cache=config.get('use_cache', True),
            fallback_enabled=config.get('fallback_enabled', True),
            confidence_threshold=config.get('confidence_threshold', 0.7),
            custom_patterns=config.get('custom_patterns', [])
        )
        
        template_path = self.templates_dir / f"{name}.json"
        save_template(template, template_path)
        print(f"\nTemplate saved: {template_path}")

    def list_templates(self) -> List[str]:
        """List available analysis templates."""
        templates = []
        for path in self.templates_dir.glob("*.json"):
            template = load_template(path)
            templates.append(f"{path.stem}: {template.description}")
        return templates

    def launch_dashboard(self, port: int = 8000) -> None:
        """Launch web dashboard for visualization."""
        # In a real implementation, this would start a web server
        # For now, we'll just create a static HTML report
        report_path = Path(__file__).parent / "reports" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path.parent.mkdir(exist_ok=True)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Framework Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2em; }}
                .framework {{ border: 1px solid #ccc; padding: 1em; margin: 1em 0; }}
                .confidence {{ color: green; }}
                .method {{ color: blue; }}
            </style>
        </head>
        <body>
            <h1>Framework Analysis Report</h1>
            <p>Generated: {datetime.now().isoformat()}</p>
            
            <h2>Analysis Results</h2>
            <div id="results">
                {self._results_to_html()}
            </div>
            
            <h2>Statistics</h2>
            <div id="stats">
                {self._stats_to_html()}
            </div>
        </body>
        </html>
        """
        
        report_path.write_text(html_content)
        webbrowser.open(f"file://{report_path}")
        print(f"\nDashboard opened in browser: {report_path}")

    def _results_to_html(self) -> str:
        """Convert analysis results to HTML."""
        if not self.current_results:
            return "<p>No analysis results available.</p>"
            
        html = []
        for fw in self.current_results.get('identified_frameworks', []):
            html.append(f"""
            <div class="framework">
                <h3>{fw['name']} ({fw['category']})</h3>
                <p class="confidence">Confidence: {fw.get('confidence_score', 'N/A')}</p>
                <p class="method">Detection Method: {fw.get('detection_method', 'N/A')}</p>
                <p>Original Text: {fw.get('original_text', 'N/A')}</p>
                {self._popularity_to_html(fw.get('popularity', {}))}
            </div>
            """)
        
        return "\n".join(html)

    def _stats_to_html(self) -> str:
        """Convert analysis statistics to HTML."""
        stats = {
            'Analysis Duration': f"{self.current_results.get('analysis_duration', 'N/A')}s",
            'Cache Hit': str(self.current_results.get('cache_hit', False)),
            'Fallback Used': str(self.current_results.get('fallback_used', False)),
            'Requires Agent': str(self.current_results.get('requires_agent', False))
        }
        
        return "\n".join(f"<p><strong>{k}:</strong> {v}</p>" for k, v in stats.items())

    def _popularity_to_html(self, popularity: Dict[str, Any]) -> str:
        """Convert popularity metrics to HTML."""
        if not popularity:
            return ""
            
        return f"""
        <div class="popularity">
            <h4>Popularity Metrics</h4>
            {' '.join(f'<p><strong>{k}:</strong> {v}</p>' for k, v in popularity.items())}
        </div>
        """

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CSS Framework Analyzer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze text for framework references')
    analyze_parser.add_argument('text', help='Text to analyze')
    analyze_parser.add_argument('--template', help='Analysis template to use')
    analyze_parser.add_argument('--output', help='Save results to file')
    analyze_parser.add_argument('--dashboard', action='store_true', help='Open results in dashboard')
    
    # Template commands
    template_parser = subparsers.add_parser('template', help='Manage analysis templates')
    template_subparsers = template_parser.add_subparsers(dest='template_command')
    
    list_parser = template_subparsers.add_parser('list', help='List available templates')
    
    create_parser = template_subparsers.add_parser('create', help='Create new template')
    create_parser.add_argument('name', help='Template name')
    create_parser.add_argument('--description', help='Template description')
    create_parser.add_argument('--no-cache', action='store_true', help='Disable result caching')
    create_parser.add_argument('--no-fallback', action='store_true', help='Disable fallback detection')
    create_parser.add_argument('--confidence', type=float, help='Confidence threshold (0.0-1.0)')
    create_parser.add_argument('--patterns', nargs='+', help='Additional regex patterns')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch web dashboard')
    dashboard_parser.add_argument('--port', type=int, default=8000, help='Dashboard port')
    
    args = parser.parse_args()
    
    cli = FrameworkAnalyzerCLI()
    
    try:
        if args.command == 'analyze':
            results = cli.analyze_text(args.text, args.template)
            cli.current_results = results
            
            # Print results
            print("\nAnalysis Results:")
            print(json.dumps(results, indent=2))
            
            # Save if requested
            if args.output:
                cli.save_results(results, args.output)
            
            # Open dashboard if requested
            if args.dashboard:
                cli.launch_dashboard()
                
        elif args.command == 'template':
            if args.template_command == 'list':
                templates = cli.list_templates()
                print("\nAvailable Templates:")
                for template in templates:
                    print(f"- {template}")
                    
            elif args.template_command == 'create':
                config = {
                    'description': args.description or '',
                    'use_cache': not args.no_cache,
                    'fallback_enabled': not args.no_fallback,
                    'confidence_threshold': args.confidence or 0.7,
                    'custom_patterns': args.patterns or []
                }
                cli.create_template(args.name, config)
                
        elif args.command == 'dashboard':
            cli.launch_dashboard(args.port)
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

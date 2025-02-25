#!/usr/bin/env python3
"""
Command-line interface for the Technology Stack Analyzer.
Provides interactive analysis and visualization of technology stack detection.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import webbrowser
from datetime import datetime

from .tech_analyzer import TechStackAnalyzer
from .templates import TemplateManager, AnalysisTemplate

class TechAnalyzerCLI:
    """Interactive CLI for Technology Stack Analysis."""

    def __init__(self) -> None:
        self.analyzer = TechStackAnalyzer(
            cache_enabled=True,
            max_cache_size=1000,
            log_level=logging.INFO
        )
        self.current_results: Dict[str, Any] = {}
        self.templates_dir = Path(__file__).parent / "templates"
        self.template_manager = TemplateManager(self.templates_dir)

    def analyze_text(self, text: str, template: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text using optional template."""
        if template:
            template_obj = self.template_manager.get_template(template)
            if template_obj:
                return self.analyzer.process_text(
                    text,
                    use_cache=template_obj.use_cache
                ).data
        
        return self.analyzer.process_text(text).data

    def save_results(self, results: Dict[str, Any], output: Optional[str] = None) -> None:
        """Save analysis results to file."""
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            results['saved_at'] = datetime.now().isoformat()
            results['cli_version'] = '1.0.2'
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")

    def create_template(self, name: str, config: Dict[str, Any]) -> None:
        """Create new analysis template."""
        template = self.template_manager.create_template(
            name=name,
            description=config.get('description', ''),
            use_cache=config.get('use_cache', True),
            confidence_threshold=config.get('confidence_threshold', 0.7),
            custom_patterns=config.get('custom_patterns', [])
        )
        print(f"\nTemplate saved: {self.templates_dir / f'{name}.json'}")

    def list_templates(self) -> List[str]:
        """List available analysis templates."""
        templates = []
        for template in self.template_manager.list_templates():
            templates.append(f"{template['name']}: {template['description']}")
        return templates

    def launch_dashboard(self, port: int = 8000) -> None:
        """Launch web dashboard for visualization."""
        # Create a static HTML report
        report_path = Path(__file__).parent / "reports" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path.parent.mkdir(exist_ok=True)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Technology Stack Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2em; }}
                .technology {{ border: 1px solid #ccc; padding: 1em; margin: 1em 0; }}
                .confidence {{ color: green; }}
                .category {{ color: blue; }}
            </style>
        </head>
        <body>
            <h1>Technology Stack Analysis Report</h1>
            <p>Generated: {datetime.now().isoformat()}</p>
            
            <h2>Analysis Results</h2>
            <div id="results">
                {self._results_to_html()}
            </div>
            
            <h2>Stack Analysis</h2>
            <div id="analysis">
                {self._analysis_to_html()}
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
        for tech in self.current_results.get('identified_technologies', []):
            html.append(f"""
            <div class="technology">
                <h3>{tech['name']} ({tech['type']})</h3>
                <p class="category">Category: {tech['category']}</p>
                <p class="confidence">Confidence: {tech.get('confidence_score', 'N/A')}</p>
                <p>Description: {tech.get('description', 'N/A')}</p>
                <p>Use Cases: {', '.join(tech.get('use_cases', []))}</p>
            </div>
            """)
        
        return "\n".join(html)

    def _analysis_to_html(self) -> str:
        """Convert stack analysis to HTML."""
        analysis = self.current_results.get('stack_analysis', {})
        if not analysis:
            return "<p>No stack analysis available.</p>"
            
        html = []
        
        # Completeness
        html.append("<h3>Stack Completeness</h3>")
        completeness = analysis.get('completeness', {})
        for category, complete in completeness.items():
            status = "✓" if complete else "✗"
            color = "green" if complete else "red"
            html.append(f'<p style="color: {color}">{status} {category.title()}</p>')
            
        # Compatibility
        html.append("<h3>Compatibility</h3>")
        compatibility = analysis.get('compatibility', {})
        score = compatibility.get('score', 1.0)
        html.append(f'<p>Compatibility Score: {score:.2f}</p>')
        
        issues = compatibility.get('issues', [])
        if issues:
            html.append("<h4>Issues:</h4>")
            html.append("<ul>")
            for issue in issues:
                html.append(f"<li>{issue}</li>")
            html.append("</ul>")
            
        # Suggestions
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            html.append("<h3>Suggestions</h3>")
            html.append("<ul>")
            for suggestion in suggestions:
                html.append(f"<li>{suggestion}</li>")
            html.append("</ul>")
        
        return "\n".join(html)

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Technology Stack Analyzer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze text for technology references')
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
    create_parser.add_argument('--confidence', type=float, help='Confidence threshold (0.0-1.0)')
    create_parser.add_argument('--patterns', nargs='+', help='Additional regex patterns')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch web dashboard')
    dashboard_parser.add_argument('--port', type=int, default=8000, help='Dashboard port')
    
    args = parser.parse_args()
    
    cli = TechAnalyzerCLI()
    
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

"""
Web dashboard for CSS Framework Analyzer.
Provides interactive visualization and analysis of framework detection results.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import socketserver
import logging
from .css_framework_analyzer import CSSFrameworkAnalyzer
from .templates import TemplateManager

# Configure logging
logger = logging.getLogger(__name__)

class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom request handler for dashboard."""
    
    def __init__(self, *args, analyzer: CSSFrameworkAnalyzer = None, **kwargs):
        self.analyzer = analyzer or CSSFrameworkAnalyzer()
        self.template_manager = TemplateManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.send_dashboard_html()
        elif self.path == '/api/templates':
            self.send_templates()
        elif self.path == '/api/stats':
            self.send_stats()
        elif self.path.startswith('/api/history'):
            self.send_history()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/analyze':
            self.handle_analysis()
        elif self.path == '/api/templates':
            self.handle_template_creation()
        else:
            self.send_error(404)

    def send_dashboard_html(self):
        """Send dashboard HTML."""
        html = self._generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def send_templates(self):
        """Send available templates."""
        templates = self.template_manager.list_templates()
        self._send_json(templates)

    def send_stats(self):
        """Send analysis statistics."""
        stats = self._get_analysis_stats()
        self._send_json(stats)

    def send_history(self):
        """Send analysis history."""
        history = self._get_analysis_history()
        self._send_json(history)

    def handle_analysis(self):
        """Handle framework analysis request."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request = json.loads(post_data.decode())
        
        text = request.get('text', '')
        template_name = request.get('template')
        
        try:
            results = self.analyzer.process_text(
                text,
                template=template_name if template_name else None
            )
            self._save_analysis_result(results)
            self._send_json(results)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self._send_json({'error': str(e)}, status=500)

    def handle_template_creation(self):
        """Handle template creation request."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        template_data = json.loads(post_data.decode())
        
        try:
            template = self.template_manager.create_template(**template_data)
            self._send_json({'status': 'success', 'template': template.to_dict()})
        except Exception as e:
            logger.error(f"Template creation failed: {e}")
            self._send_json({'error': str(e)}, status=500)

    def _send_json(self, data: Any, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CSS Framework Analyzer Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body class="bg-gray-100">
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-3xl font-bold mb-8">CSS Framework Analyzer Dashboard</h1>
                
                <!-- Analysis Form -->
                <div class="card p-6 mb-8">
                    <h2 class="text-xl font-semibold mb-4">New Analysis</h2>
                    <form id="analysisForm" class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium mb-2">Text to Analyze</label>
                            <textarea id="text" class="w-full p-2 border rounded" rows="4"></textarea>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Template</label>
                            <select id="template" class="w-full p-2 border rounded">
                                <option value="">None</option>
                            </select>
                        </div>
                        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            Analyze
                        </button>
                    </form>
                </div>
                
                <!-- Results -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <!-- Current Analysis -->
                    <div class="card p-6">
                        <h2 class="text-xl font-semibold mb-4">Current Analysis</h2>
                        <div id="currentResults" class="space-y-4"></div>
                    </div>
                    
                    <!-- Statistics -->
                    <div class="card p-6">
                        <h2 class="text-xl font-semibold mb-4">Statistics</h2>
                        <canvas id="statsChart"></canvas>
                    </div>
                </div>
                
                <!-- History -->
                <div class="card p-6 mt-8">
                    <h2 class="text-xl font-semibold mb-4">Analysis History</h2>
                    <div id="history" class="space-y-4"></div>
                </div>
            </div>

            <script>
                // Dashboard JavaScript
                document.addEventListener('DOMContentLoaded', () => {{
                    // Load templates
                    fetch('/api/templates')
                        .then(res => res.json())
                        .then(templates => {{
                            const select = document.getElementById('template');
                            templates.forEach(t => {{
                                const option = document.createElement('option');
                                option.value = t.name;
                                option.textContent = `${{t.name}} - ${{t.description}}`;
                                select.appendChild(option);
                            }});
                        }});
                    
                    // Handle analysis form
                    document.getElementById('analysisForm').addEventListener('submit', async (e) => {{
                        e.preventDefault();
                        const text = document.getElementById('text').value;
                        const template = document.getElementById('template').value;
                        
                        try {{
                            const res = await fetch('/api/analyze', {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{ text, template }})
                            }});
                            const results = await res.json();
                            displayResults(results);
                            updateStats();
                            updateHistory();
                        }} catch (err) {{
                            console.error('Analysis failed:', err);
                            alert('Analysis failed: ' + err.message);
                        }}
                    }});
                    
                    // Initial data load
                    updateStats();
                    updateHistory();
                }});

                function displayResults(results) {{
                    const container = document.getElementById('currentResults');
                    container.innerHTML = '';
                    
                    if (results.identified_frameworks.length === 0) {{
                        container.innerHTML = '<p class="text-gray-500">No frameworks detected</p>';
                        return;
                    }}
                    
                    results.identified_frameworks.forEach(fw => {{
                        const div = document.createElement('div');
                        div.className = 'p-4 border rounded';
                        div.innerHTML = `
                            <h3 class="font-semibold">${{fw.name}} (${{fw.category}})</h3>
                            <p class="text-sm text-gray-600">Confidence: ${{fw.confidence_score}}</p>
                            <p class="text-sm text-gray-600">Method: ${{fw.detection_method}}</p>
                        `;
                        container.appendChild(div);
                    }});
                }}

                async function updateStats() {{
                    const res = await fetch('/api/stats');
                    const stats = await res.json();
                    
                    const ctx = document.getElementById('statsChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: Object.keys(stats.framework_counts),
                            datasets: [{{
                                label: 'Framework Detections',
                                data: Object.values(stats.framework_counts),
                                backgroundColor: 'rgba(59, 130, 246, 0.5)'
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            scales: {{
                                y: {{
                                    beginAtZero: true,
                                    ticks: {{
                                        stepSize: 1
                                    }}
                                }}
                            }}
                        }}
                    }});
                }}

                async function updateHistory() {{
                    const res = await fetch('/api/history');
                    const history = await res.json();
                    
                    const container = document.getElementById('history');
                    container.innerHTML = '';
                    
                    history.forEach(entry => {{
                        const div = document.createElement('div');
                        div.className = 'p-4 border rounded';
                        div.innerHTML = `
                            <p class="text-sm text-gray-500">${{new Date(entry.timestamp).toLocaleString()}}</p>
                            <p class="font-medium">${{entry.frameworks.join(', ') || 'No frameworks detected'}}</p>
                            <p class="text-sm text-gray-600">Analysis duration: ${{entry.duration}}s</p>
                        `;
                        container.appendChild(div);
                    }});
                }}
            </script>
        </body>
        </html>
        """

    def _get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        history_file = Path(__file__).parent / "data" / "analysis_history.json"
        if not history_file.exists():
            return {
                'framework_counts': {},
                'total_analyses': 0,
                'avg_duration': 0
            }
            
        with open(history_file) as f:
            history = json.load(f)
            
        framework_counts = {}
        total_duration = 0
        
        for entry in history:
            for fw in entry.get('frameworks', []):
                framework_counts[fw] = framework_counts.get(fw, 0) + 1
            total_duration += entry.get('duration', 0)
            
        return {
            'framework_counts': framework_counts,
            'total_analyses': len(history),
            'avg_duration': total_duration / len(history) if history else 0
        }

    def _get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history."""
        history_file = Path(__file__).parent / "data" / "analysis_history.json"
        if not history_file.exists():
            return []
            
        with open(history_file) as f:
            return json.load(f)

    def _save_analysis_result(self, results: Dict[str, Any]) -> None:
        """Save analysis result to history."""
        history_file = Path(__file__).parent / "data" / "analysis_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        history = []
        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)
                
        # Add new entry
        history.append({
            'timestamp': datetime.now().isoformat(),
            'frameworks': [
                fw['name'] for fw in results.get('identified_frameworks', [])
            ],
            'duration': results.get('analysis_duration', 0),
            'cache_hit': results.get('cache_hit', False),
            'fallback_used': results.get('fallback_used', False)
        })
        
        # Keep only last 100 entries
        history = history[-100:]
        
        # Save atomically
        temp_file = history_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(history, f, indent=2)
        temp_file.rename(history_file)

class DashboardServer:
    """Web server for the dashboard."""

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8000,
        analyzer: Optional[CSSFrameworkAnalyzer] = None
    ):
        """Initialize dashboard server."""
        self.host = host
        self.port = port
        self.analyzer = analyzer or CSSFrameworkAnalyzer()
        self.server = None
        self.thread = None

    def start(self) -> None:
        """Start the dashboard server."""
        handler = lambda *args: DashboardHandler(*args, analyzer=self.analyzer)
        
        class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
            """Threaded HTTP server."""
            pass
            
        self.server = ThreadedHTTPServer((self.host, self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Dashboard server running at http://{self.host}:{self.port}")
        webbrowser.open(f"http://{self.host}:{self.port}")

    def stop(self) -> None:
        """Stop the dashboard server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Dashboard server stopped")

def launch_dashboard(
    host: str = 'localhost',
    port: int = 8000,
    analyzer: Optional[CSSFrameworkAnalyzer] = None
) -> None:
    """Launch the dashboard in a browser."""
    server = DashboardServer(host, port, analyzer)
    try:
        server.start()
        input("Press Enter to stop the dashboard server...\n")
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()

if __name__ == '__main__':
    launch_dashboard()

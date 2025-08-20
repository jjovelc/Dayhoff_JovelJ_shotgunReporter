#!/usr/bin/env python3
"""
Simple HTTP server to handle the extract_taxa.py script calls for the web interface.
This allows the HTML page to fetch taxa data and create visualizations.
"""

import http.server
import socketserver
import urllib.parse
import subprocess
import json
import os
from pathlib import Path

class TaxaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        # Handle API calls to extract_taxa.py
        if path == '/cgi-bin/extract_taxa.py':
            self.handle_taxa_request(query)
        elif path == '/cgi-bin/taxa_comparison.py':
            self.handle_taxa_comparison_request(query)
        elif path.endswith('.md'):
            # Handle markdown files with proper content type
            self.serve_markdown_file(path)
        else:
            # Serve static files normally
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for AI analysis"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/cgi-bin/ai_analyze.py':
            self.handle_ai_analysis_request()
        elif path == '/cgi-bin/ai_summary.py':
            self.handle_ai_summary_request()
        else:
            self.send_error(405, "Method not allowed")
    
    def serve_markdown_file(self, path):
        """Serve markdown files as rendered HTML"""
        try:
            # Remove leading slash and get file path
            file_path = path.lstrip('/')
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return
            
            # Read the markdown content
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert markdown to HTML
            import markdown
            html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code', 'codehilite'])
            
            # Create a complete HTML document with proper styling
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.basename(file_path)} - Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #ecf0f1;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        ul, ol {{
            padding-left: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .header {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 20px;
            margin: -40px -40px 30px -40px;
            border-radius: 12px 12px 0 0;
        }}
        .header h1 {{
            margin: 0;
            border: none;
            padding: 0;
        }}

    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 {os.path.basename(file_path)}</h1>
        </div>

        {html_content}
    </div>
</body>
</html>"""
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(full_html.encode('utf-8'))))
            self.end_headers()
            
            # Write HTML content
            self.wfile.write(full_html.encode('utf-8'))
            
        except Exception as e:
            print(f"Error serving markdown file {path}: {e}")
            self.send_error(500, f"Internal server error: {e}")
    
    def handle_ai_analysis_request(self):
        """Handle AI analysis requests"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                # Read POST data
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # Parse form data (simple parsing for multipart/form-data)
                form_data = {}
                if 'multipart/form-data' in self.headers.get('Content-Type', ''):
                    # Parse multipart form data
                    boundary = self.headers.get('Content-Type').split('boundary=')[1]
                    parts = post_data.split('--' + boundary)
                    
                    for part in parts:
                        if 'name=' in part and 'Content-Type:' not in part:
                            lines = part.strip().split('\r\n')
                            if len(lines) >= 3:
                                name_line = lines[0]
                                value = lines[-1]
                                
                                if 'name="' in name_line:
                                    name = name_line.split('name="')[1].split('"')[0]
                                    form_data[name] = value
                
                # Call AI analyzer
                result = self.run_ai_analyzer(form_data)
                self.send_json_response(result)
            else:
                self.send_error_response('No data received')
                
        except Exception as e:
            self.send_error_response(f'AI analysis error: {str(e)}')
    
    def run_ai_analyzer(self, form_data):
        """Run the AI analyzer with form data"""
        try:
            # Import and use the AI analyzer
            import sys
            import importlib
            sys.path.append(os.getcwd())
            
            # Force reload the module to get latest changes
            if 'ai_realtime_analyzer' in sys.modules:
                importlib.reload(sys.modules['ai_realtime_analyzer'])
            
            from ai_realtime_analyzer import RealTimeMicrobiomeAnalyzer
            
            analyzer = RealTimeMicrobiomeAnalyzer()
            
            plot_type = form_data.get('plot_type', '')
            taxon_name = form_data.get('taxon_name', '')
            taxonomic_level = form_data.get('taxonomic_level', '')
            
            if plot_type == 'taxon_plot' and taxon_name:
                # Parse JSON data
                import json
                sample_data = json.loads(form_data.get('sample_data', '{}'))
                sample_names = json.loads(form_data.get('sample_names', '[]'))
                rpm_values = json.loads(form_data.get('rpm_values', '[]'))
                
                analysis = analyzer.analyze_taxon_plot(taxon_name, sample_data, sample_names, rpm_values)
                
                return {
                    'success': True,
                    'analysis': analysis,
                    'plot_type': plot_type,
                    'taxon_name': taxon_name
                }
                
            elif plot_type == 'alpha_diversity':
                # Extract actual diversity data and analyze
                if not taxonomic_level:
                    taxonomic_level = 'phylum'  # Default to phylum level
                
                diversity_data = analyzer.extract_alpha_diversity_data(taxonomic_level)
                
                if diversity_data:
                    analysis = analyzer.analyze_diversity_plot(plot_type, diversity_data)
                    return {
                        'success': True,
                        'analysis': analysis,
                        'plot_type': plot_type,
                        'taxonomic_level': taxonomic_level,
                        'data_points': len(diversity_data)
                    }
                else:
                    # Fallback if data extraction fails
                    analysis = analyzer._generate_fallback_diversity_analysis(plot_type, {})
                    return {
                        'success': True,
                        'analysis': analysis,
                        'plot_type': plot_type,
                        'taxonomic_level': taxonomic_level,
                        'data_points': 0
                    }
                    
            elif plot_type == 'pcoa':
                # Extract actual abundance data and analyze
                if not taxonomic_level:
                    taxonomic_level = 'phylum'  # Default to phylum level
                
                abundances = analyzer.extract_pcoa_data(taxonomic_level)
                
                if abundances:
                    analysis = analyzer.analyze_pcoa_plot(plot_type, abundances)
                    return {
                        'success': True,
                        'analysis': analysis,
                        'plot_type': plot_type,
                        'taxonomic_level': taxonomic_level,
                        'data_points': len(abundances)
                    }
                else:
                    # Fallback if data extraction fails
                    analysis = analyzer._generate_fallback_pcoa_analysis(plot_type, {})
                    return {
                        'success': True,
                        'analysis': analysis,
                        'plot_type': plot_type,
                        'taxonomic_level': taxonomic_level,
                        'data_points': 0
                    }
                    
            elif plot_type == 'stacked_barplot':
                # Extract actual abundance data and analyze
                if not taxonomic_level:
                    taxonomic_level = 'phylum'  # Default to phylum level
                
                top_taxa, abundances = analyzer.extract_stacked_barplot_data(taxonomic_level)
                
                if top_taxa and abundances:
                    analysis = analyzer.analyze_stacked_plot(plot_type, top_taxa, abundances)
                    return {
                        'success': True,
                        'analysis': analysis,
                        'plot_type': plot_type,
                        'taxonomic_level': taxonomic_level,
                        'top_taxa_count': len(top_taxa),
                        'sample_count': len(abundances)
                    }
                else:
                    # Fallback if data extraction fails
                    analysis = analyzer._generate_fallback_stacked_analysis(plot_type, [], {})
                    return {
                        'success': True,
                        'analysis': analysis,
                        'plot_type': plot_type,
                        'taxonomic_level': taxonomic_level,
                        'top_taxa_count': 0,
                        'sample_count': 0
                    }
            else:
                return {
                    'success': False,
                    'error': 'Invalid plot type or missing parameters'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'type': 'server_error'
            }
    
    def handle_taxa_request(self, query):
        """Handle requests to the extract_taxa.py script"""
        try:
            command = query.get('command', [None])[0]
            
            if command == 'get_taxa':
                level = query.get('level', [None])[0]
                if level:
                    result = self.run_extract_taxa('get_taxa', level)
                    self.send_json_response(result)
                else:
                    self.send_error_response('Missing level parameter')
                    
            elif command == 'get_data':
                level = query.get('level', [None])[0]
                taxon = query.get('taxon', [None])[0]
                if level and taxon:
                    result = self.run_extract_taxa('get_data', level, taxon)
                    self.send_json_response(result)
                else:
                    self.send_error_response('Missing level or taxon parameter')
                    
            else:
                self.send_error_response('Invalid command')
                
        except Exception as e:
            self.send_error_response(f'Server error: {str(e)}')
    
    def handle_taxa_comparison_request(self, query):
        """Handle requests for taxa comparison tables"""
        try:
            command = query.get('command', [None])[0]
            level = query.get('level', [None])[0]
            format_type = query.get('format', ['tsv'])[0]  # Default to TSV
            
            if not command or not level:
                self.send_error_response('Missing command or level parameter')
                return
            
            if command == 'get_comparison':
                if format_type == 'tsv':
                    self.send_taxa_comparison_tsv(level)
                elif format_type == 'excel':
                    self.send_taxa_comparison_excel(level)
                else:
                    self.send_error_response('Invalid format. Use "tsv" or "excel"')
            else:
                self.send_error_response('Invalid command')
                
        except Exception as e:
            self.send_error_response(f'Server error: {str(e)}')
    
    def send_taxa_comparison_tsv(self, level):
        """Send taxa comparison data as TSV"""
        try:
            # Import and use the AI analyzer
            import sys
            import importlib
            sys.path.append(os.getcwd())
            
            # Force reload the module to get latest changes
            if 'ai_realtime_analyzer' in sys.modules:
                importlib.reload(sys.modules['ai_realtime_analyzer'])
            
            from ai_realtime_analyzer import RealTimeMicrobiomeAnalyzer
            
            analyzer = RealTimeMicrobiomeAnalyzer()
            
            # Map level number to taxonomic level name
            level_mapping = {
                "2": "phylum", "3": "class", "4": "order", 
                "5": "family", "6": "genus", "7": "species"
            }
            
            taxonomic_level = level_mapping.get(level, "family")
            
            # Generate TSV content
            print(f"DEBUG: Calling generate_taxa_comparison_tsv for level: {taxonomic_level}", file=sys.stderr)
            tsv_content = analyzer.generate_taxa_comparison_tsv(taxonomic_level)
            print(f"DEBUG: TSV content length: {len(tsv_content) if tsv_content else 0}", file=sys.stderr)
            print(f"DEBUG: TSV first line: {tsv_content.split(chr(10))[0] if tsv_content else 'None'}", file=sys.stderr)
            
            if not tsv_content:
                self.send_error_response('No data available for this taxonomic level')
                return
            
            # Send TSV response
            filename = f"taxa_comparison_{taxonomic_level}.tsv"
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/tab-separated-values')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(tsv_content.encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f'Error generating TSV: {str(e)}')
    
    def send_taxa_comparison_excel(self, level):
        """Send taxa comparison data as Excel"""
        try:
            # Import and use the AI analyzer
            import sys
            import importlib
            sys.path.append(os.getcwd())
            
            # Force reload the module to get latest changes
            if 'ai_realtime_analyzer' in sys.modules:
                importlib.reload(sys.modules['ai_realtime_analyzer'])
            
            from ai_realtime_analyzer import RealTimeMicrobiomeAnalyzer
            
            analyzer = RealTimeMicrobiomeAnalyzer()
            
            # Map level number to taxonomic level name
            level_mapping = {
                "2": "phylum", "3": "class", "4": "order", 
                "5": "family", "6": "genus", "7": "species"
            }
            
            taxonomic_level = level_mapping.get(level, "family")
            
            # Generate Excel content
            excel_content = analyzer.generate_taxa_comparison_excel(taxonomic_level)
            
            if not excel_content:
                self.send_error_response('No data available for this taxonomic level')
                return
            
            # Send Excel response
            filename = f"taxa_comparison_{taxonomic_level}.xlsx"
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(excel_content)
            
        except Exception as e:
            self.send_error_response(f'Error generating Excel: {str(e)}')
    
    def run_extract_taxa(self, command, *args):
        """Run the extract_taxa.py script with given arguments"""
        try:
            cmd = ['python3', 'extract_taxa_simple.py', command] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                # Try to parse as JSON
                try:
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError:
                    # If not JSON, return as string
                    return result.stdout.strip()
            else:
                return {'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
    
    def handle_ai_summary_request(self):
        """Handle AI summary generation requests"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                # Read POST data
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # Parse form data (simple parsing for multipart/form-data)
                form_data = {}
                if 'multipart/form-data' in self.headers.get('Content-Type', ''):
                    # Parse multipart form data
                    boundary = self.headers.get('Content-Type').split('boundary=')[1]
                    parts = post_data.split('--' + boundary)
                    
                    for part in parts:
                        if 'name=' in part and 'Content-Type:' not in part:
                            lines = part.strip().split('\r\n')
                            if len(lines) >= 3:
                                name_line = lines[0]
                                value = lines[-1]
                                
                                if 'name="' in name_line:
                                    name = name_line.split('name="')[1].split('"')[0]
                                    form_data[name] = value
                
                # Call AI summary generator
                result = self.run_ai_summary_generator(form_data)
                self.send_json_response(result)
            else:
                self.send_error_response('No data received')
                
        except Exception as e:
            self.send_error_response(f'AI summary error: {str(e)}')
    
    def run_ai_summary_generator(self, form_data):
        """Run the AI summary generator with form data"""
        try:
            # Import and use the AI analyzer
            import sys
            import importlib
            sys.path.append(os.getcwd())
            
            # Force reload the module to get latest changes
            if 'ai_realtime_analyzer' in sys.modules:
                importlib.reload(sys.modules['ai_realtime_analyzer'])
            
            from ai_realtime_analyzer import RealTimeMicrobiomeAnalyzer
            
            analyzer = RealTimeMicrobiomeAnalyzer()
            
            taxonomic_level = form_data.get('taxonomic_level', '')
            report_type = form_data.get('report_type', 'technical')
            
            if not taxonomic_level:
                return {'success': False, 'error': 'Missing taxonomic_level parameter'}
            
            # Generate AI summary
            ai_summary = analyzer.generate_ai_summary(taxonomic_level, report_type)
            
            if not ai_summary or ai_summary.startswith("Error"):
                return {'success': False, 'error': ai_summary}
            
            # Generate PDF report
            try:
                # Import the PDF generation function
                import sys
                sys.path.append(os.path.join(os.getcwd(), 'cgi-bin'))
                
                # Import the PDF creation function from ai_summary.py
                from ai_summary import create_pdf_report
                
                # Create PDF
                pdf_content = create_pdf_report(analyzer, taxonomic_level, report_type, ai_summary)
                
                if pdf_content:
                    # Encode PDF content
                    import base64
                    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
                    
                    return {
                        'success': True,
                        'message': f'AI summary generated successfully for {taxonomic_level} level',
                        'report_type': report_type,
                        'pdf_data': pdf_base64
                    }
                else:
                    return {'success': False, 'error': 'Failed to generate PDF'}
                    
            except Exception as e:
                print(f"PDF generation error: {e}", file=sys.stderr)
                # Fallback to text summary if PDF generation fails
                return {
                    'success': True,
                    'message': f'AI summary generated successfully for {taxonomic_level} level (text only)',
                    'report_type': report_type,
                    'summary': ai_summary
                }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if isinstance(data, str):
            # If data is a string, try to parse it as JSON
            try:
                json_data = json.loads(data)
                self.wfile.write(json.dumps(json_data).encode())
            except json.JSONDecodeError:
                # If it's not JSON, wrap it in a response object
                response = {'result': data}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, message):
        """Send error response"""
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())

def main():
    """Main function to start the server"""
    PORT = 8001
    
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    with socketserver.TCPServer(("", PORT), TaxaRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Open index.html in your browser to use the interface")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    main()

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
        else:
            # Serve static files normally
            super().do_GET()
    
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
    PORT = 8000
    
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

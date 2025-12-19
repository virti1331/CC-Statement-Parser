"""
Vercel Serverless Function - Credit Card Statement Parser
Entry point: /api/index (maps to /api/)
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json
import tempfile
import os
import sys
import cgi
from io import BytesIO

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import parsing modules
from main import parse_statement
from parser.detect_issuer import UnsupportedIssuerError

class handler(BaseHTTPRequestHandler):
    """Handler for Vercel serverless function"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for PDF parsing"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_error_response(400, "Content-Type must be multipart/form-data")
                return
            
            # Parse form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )
            
            # Check if file exists
            if 'file' not in form:
                self.send_error_response(400, "No file part in the request.")
                return
            
            file_item = form['file']
            
            if not file_item.filename:
                self.send_error_response(400, "No file selected.")
                return
            
            # Validate PDF extension
            if not file_item.filename.lower().endswith('.pdf'):
                self.send_error_response(400, "Unsupported file type. Please upload a PDF.")
                return
            
            # Save to temporary file
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file_item.file.read())
                    tmp_path = tmp.name
                
                # Parse the statement
                parsed_data = parse_statement(tmp_path)
                
                # Send success response
                self.send_success_response({
                    "success": True,
                    "file": file_item.filename,
                    "data": parsed_data
                })
                
            finally:
                # Cleanup temp file
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except:
                        pass
        
        except UnsupportedIssuerError as e:
            self.send_error_response(400, str(e))
        
        except Exception as e:
            self.send_error_response(500, f"Failed to parse statement: {str(e)}")
    
    def send_success_response(self, data):
        """Send JSON success response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, status_code, error_message):
        """Send JSON error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            "success": False,
            "error": error_message
        }
        self.wfile.write(json.dumps(response).encode())

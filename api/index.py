"""
Vercel Serverless Function - Credit Card Statement Parser
Properly handles multipart file uploads in serverless environment
"""

import json
import tempfile
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import parsing modules
from main import parse_statement
from parser.detect_issuer import UnsupportedIssuerError


def handler(event, context):
    """
    Main handler for Vercel Python serverless function
    Compatible with Vercel's Python runtime
    """
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS' or event.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # Only accept POST
    method = event.get('httpMethod') or event.get('method', '')
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'success': False, 'error': 'Method not allowed'})
        }
    
    try:
        # Get the request body
        body = event.get('body', '')
        headers = event.get('headers', {})
        
        # Check content type
        content_type = headers.get('content-type', '') or headers.get('Content-Type', '')
        
        if 'multipart/form-data' not in content_type:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'success': False, 'error': 'Content-Type must be multipart/form-data'})
            }
        
        # Parse multipart data
        import cgi
        from io import BytesIO
        
        # Create a file-like object from the body
        if event.get('isBase64Encoded'):
            import base64
            body_bytes = base64.b64decode(body)
        else:
            body_bytes = body.encode() if isinstance(body, str) else body
        
        environ = {
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': str(len(body_bytes))
        }
        
        fp = BytesIO(body_bytes)
        form = cgi.FieldStorage(fp=fp, environ=environ, headers={'content-type': content_type})
        
        # Check if file exists
        if 'file' not in form:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'success': False, 'error': 'No file part in the request'})
            }
        
        file_item = form['file']
        
        if not file_item.filename:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'success': False, 'error': 'No file selected'})
            }
        
        # Validate PDF
        if not file_item.filename.lower().endswith('.pdf'):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'success': False, 'error': 'Unsupported file type. Please upload a PDF'})
            }
        
        # Save and parse
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_item.file.read())
                tmp_path = tmp.name
            
            # Parse the statement
            parsed_data = parse_statement(tmp_path)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'success': True,
                    'file': file_item.filename,
                    'data': parsed_data
                })
            }
            
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
    
    except UnsupportedIssuerError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'success': False, 'error': str(e)})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'success': False, 'error': f'Failed to parse statement: {str(e)}'})
        }

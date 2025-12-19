"""
Vercel serverless function for parsing credit card statements.
This function handles POST requests to /api/parse
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import tempfile
import os

# Import local modules
from main import parse_statement
from parser.detect_issuer import UnsupportedIssuerError

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename: str) -> bool:
    """Check if the file has a valid PDF extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/parse", methods=["POST", "OPTIONS"])
@app.route("/", methods=["POST", "OPTIONS"])
def handler():
    """
    Main handler for parsing credit card statements.
    Accepts multipart/form-data with a 'file' field containing a PDF.
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200
    
    # Validate file presence
    if "file" not in request.files:
        response = jsonify({
            "success": False, 
            "error": "No file part in the request."
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 400

    file = request.files["file"]

    if file.filename == "":
        response = jsonify({
            "success": False, 
            "error": "No file selected."
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 400

    if not allowed_file(file.filename):
        response = jsonify({
            "success": False, 
            "error": "Unsupported file type. Please upload a PDF."
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 400

    filename = secure_filename(file.filename)
    tmp_path = None
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Parse the statement
        parsed = parse_statement(tmp_path)
        
        response = jsonify({
            "success": True, 
            "file": filename, 
            "data": parsed
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 200

    except UnsupportedIssuerError as e:
        response = jsonify({
            "success": False, 
            "error": str(e)
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 400
        
    except Exception as e:
        response = jsonify({
            "success": False, 
            "error": f"Failed to parse statement: {str(e)}"
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500
        
    finally:
        # Cleanup temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

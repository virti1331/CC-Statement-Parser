from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys

# Add backend parser modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import parse_statement
from backend.parser.detect_issuer import UnsupportedIssuerError

app = FastAPI(title="Credit Card Parser API")

# CORS - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "CC Parser Backend Live",
        "version": "1.0",
        "supported_banks": ["HDFC", "ICICI", "Axis", "Chase", "IDFC"]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Parse uploaded credit card statement PDF
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    tmp_path = None
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse the statement using existing parser logic
        parsed_data = parse_statement(tmp_path)
        
        return {
            "success": True,
            "file": file.filename,
            "data": parsed_data
        }
    
    except UnsupportedIssuerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse statement: {str(e)}")
    
    finally:
        # Cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

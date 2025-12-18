# Credit Card Statement Parser

A Python-based application that automatically extracts structured data from credit card statement PDFs. Supports multiple banks and provides both a web interface and command-line tool.

## Project Scope

### What It Does

This application parses credit card statement PDFs and extracts key information including:
- **Issuer identification** (which bank issued the card)
- **Card details** (last 4 digits of card number)
- **Billing information** (billing period, payment due date)
- **Financial data** (total amount due)
- **Transaction history** (date, description, amount for each transaction)

### Problem It Solves

Manually extracting data from credit card statements is time-consuming and error-prone. This tool automates the process by:
- Reading PDF statements directly
- Identifying the bank automatically
- Extracting structured data using bank-specific parsers
- Providing results in JSON format for easy integration

### Use Cases

- **Personal Finance Tracking**: Quickly extract spending data from multiple statements
- **Expense Analysis**: Parse transactions for budgeting and analysis
- **Data Integration**: Get structured data from PDFs for spreadsheets or databases
- **Batch Processing**: Process multiple statements via CLI

## Technologies Used

### Backend

- **Python 3.8+**: Core programming language
- **Flask 3.0.0**: Lightweight web framework for API and static file serving
- **pdfplumber 0.10.3**: PDF text extraction library
- **gunicorn 21.2.0**: Production WSGI server (optional, for deployment)

### Frontend

- **HTML5**: Web interface structure
- **JavaScript (Vanilla)**: Client-side logic and API communication
- **Tailwind CSS**: Modern styling via CDN

### Architecture

- **RESTful API**: Simple POST endpoint for PDF parsing
- **Single-Page Application**: Frontend served as static files
- **Modular Parser Design**: Separate parser module for each bank

## Project Structure

```
CC Statement Parser/
│
├── backend/                    # Backend application
│   ├── app.py                  # Flask web server
│   │   ├── Serves frontend files
│   │   ├── Handles /api/parse endpoint
│   │   └── CORS configuration
│   │
│   ├── main.py                 # CLI entry point
│   │   ├── Command-line interface
│   │   ├── parse_statement() function
│   │   └── JSON output formatting
│   │
│   ├── wsgi.py                 # Production WSGI entry point
│   │   └── For gunicorn deployment
│   │
│   ├── parser/                 # Parser modules
│   │   ├── __init__.py         # Package exports
│   │   ├── detect_issuer.py    # Bank detection logic
│   │   │   └── Identifies issuer from PDF text
│   │   │
│   │   ├── utils.py            # Shared utilities
│   │   │   ├── extract_text_from_pdf()
│   │   │   ├── find_pattern() - regex helpers
│   │   │   └── Text processing functions
│   │   │
│   │   ├── hdfc.py             # HDFC Bank parser
│   │   ├── icici.py             # ICICI Bank parser
│   │   ├── axis.py              # Axis Bank parser
│   │   ├── chase.py             # Chase Bank parser
│   │   └── idfc.py              # IDFC First Bank parser
│   │       └── Each parser extracts: issuer, card, dates, amounts, transactions
│   │
│   ├── requirements.txt        # Python dependencies
│   │
│   └── samples/                # Sample PDF statements for testing
│       ├── HDFC_statement.pdf
│       ├── ICICI_statement.pdf
│       ├── axisbank_statement.pdf
│       ├── chase_statement.pdf
│       └── IDFC_statement.pdf
│
├── frontend/                   # Frontend application
│   └── index.html              # Single-page web interface
│       ├── File upload UI
│       ├── API integration
│       ├── Results display
│       └── Transaction filtering
│
└── README.md                   # This file
```

### Component Details

#### Backend Components

**`app.py`** - Flask Web Server
- Creates Flask application instance
- Serves frontend static files from `frontend/` directory
- Handles `/api/parse` POST endpoint for PDF uploads
- Manages file uploads, temporary file cleanup, and error handling
- Configures CORS headers for cross-origin requests

**`main.py`** - CLI Tool
- Entry point for command-line usage
- Accepts PDF file path as argument
- Orchestrates parsing workflow:
  1. Extract text from PDF
  2. Detect bank issuer
  3. Route to appropriate parser
  4. Return structured JSON
- Logs operations to `parser.log`

**`parser/detect_issuer.py`** - Bank Detection
- Searches PDF text for bank-specific keywords
- Returns issuer code (HDFC, ICICI, AXIS, CHASE, IDFC)
- Raises `UnsupportedIssuerError` if bank not recognized

**`parser/utils.py`** - Shared Utilities
- `extract_text_from_pdf()`: Uses pdfplumber to extract all text
- `find_pattern()`: Regex pattern matching helpers
- Text processing and normalization functions

**Bank Parsers** (`hdfc.py`, `icici.py`, etc.)
- Each module contains issuer-specific parsing logic
- Uses regex patterns tailored to that bank's statement format
- Extracts: issuer, card_last_4_digits, billing_period, payment_due_date, total_amount_due, transactions
- Returns `None` for missing fields (graceful degradation)

#### Frontend Component

**`index.html`** - Web Interface
- Single HTML file with embedded CSS (Tailwind CDN) and JavaScript
- File upload interface
- Calls `/api/parse` endpoint
- Displays parsed results in formatted cards
- Transaction table with filtering capabilities
- Responsive design for mobile and desktop

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Install dependencies
pip install -r backend/requirements.txt
```

## Usage

### Web Interface

```bash
# Start the server
cd backend
python app.py

# Open in browser
# http://localhost:5000
```

1. Click "Upload" and select a PDF statement
2. Click "Parse statement"
3. View extracted data and transactions

### Command Line

```bash
cd backend
python main.py path/to/statement.pdf
```

Output is printed as formatted JSON to the console.

### API Endpoint

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "file=@statement.pdf"
```

**Response:**
```json
{
  "success": true,
  "file": "statement.pdf",
  "data": {
    "issuer": "HDFC",
    "card_last_4_digits": "4341",
    "billing_period": "23/10/2024",
    "payment_due_date": "12/11/2024",
    "total_amount_due": "₹83,794.00",
    "transactions": [...]
  }
}
```

## Supported Banks

- **HDFC Bank** - India
- **ICICI Bank** - India
- **Axis Bank** - India
- **Chase Bank** - USA
- **IDFC First Bank** - India

## How It Works

1. **PDF Text Extraction**: Uses `pdfplumber` to extract all text from PDF pages
2. **Bank Detection**: Searches extracted text for bank-specific keywords
3. **Parser Selection**: Routes to the appropriate bank-specific parser
4. **Field Extraction**: Uses regex patterns to find and extract:
   - Card number (last 4 digits)
   - Billing period dates
   - Payment due date
   - Total amount due
   - Individual transactions
5. **Data Return**: Returns structured JSON with all extracted information

## Limitations

- **Text-based PDFs only**: Does not support scanned/image-based PDFs (no OCR)
- **Format-specific**: Parsers are designed for specific statement layouts
- **Bank format changes**: If a bank changes their statement format, the parser may need updates
- **Date formats**: Dates are preserved as-is from the PDF (not normalized)

## Production Deployment

For production, use a WSGI server:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 backend.wsgi:app
```

Or set environment variables:
```bash
export PORT=5000
export FLASK_DEBUG=false
python backend/app.py
```

## Notes

- Always verify parsed data against original statements
- Works best with text-based PDFs (not scanned documents)
- Sample PDFs are available in `backend/samples/` for testing

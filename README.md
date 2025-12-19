# Credit Card Statement Parser

Automated PDF parser for extracting structured transaction data from credit card statements with multi-bank support.

## Overview

This application parses credit card statement PDFs and extracts structured data including card details, billing information, payment due dates, total amounts, and transaction history. It automatically detects the issuing bank and returns results in JSON format.

**Key Capabilities:**
- Automatic bank detection from PDF content
- Multi-bank support (5 major banks)
- Transaction-level extraction with dates, descriptions, and amounts
- RESTful API and CLI interface
- Web-based UI for easy file uploads

## Supported Banks

| Bank | Country | Code |
|------|---------|------|
| HDFC Bank | India | `HDFC` |
| ICICI Bank | India | `ICICI` |
| Axis Bank | India | `AXIS` |
| Chase Bank | USA | `CHASE` |
| IDFC First Bank | India | `IDFC` |

## Technology Stack

- **Backend:** Python 3.8+, Flask 3.0.0, pdfplumber 0.10.3
- **Frontend:** HTML5, JavaScript, Tailwind CSS
- **Architecture:** RESTful API, modular parser design

## Project Structure

```
backend/
├── app.py              # Flask web server & API
├── main.py             # CLI interface & core parser
├── wsgi.py             # Production WSGI entry point
├── parser/
│   ├── detect_issuer.py   # Bank detection engine
│   ├── utils.py           # PDF extraction utilities
│   ├── hdfc.py            # HDFC Bank parser
│   ├── icici.py           # ICICI Bank parser
│   ├── axis.py            # Axis Bank parser
│   ├── chase.py           # Chase Bank parser
│   └── idfc.py            # IDFC First Bank parser
├── requirements.txt
└── samples/           # Sample PDF statements

frontend/
└── index.html         # Web interface
```

## Installation

```bash
# Clone repository
git clone https://github.com/virti1331/cc-statement-parser.git
cd cc-statement-parser

# Install dependencies
pip install -r backend/requirements.txt

# Start server
cd backend
python app.py
```

Access at: http://localhost:5000

## Usage

### Web Interface

1. Navigate to http://localhost:5000
2. Upload PDF statement (drag-and-drop or browse)
3. Click "Parse Statement"
4. View extracted data and transactions

### Command Line

```bash
cd backend
python main.py samples/HDFC_statement.pdf
```

### API Endpoint

**POST** `/api/parse`

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
    "billing_period": "01/10/2024 - 31/10/2024",
    "payment_due_date": "15/11/2024",
    "total_amount_due": "₹83,794.00",
    "transactions": [
      {
        "date": "24/10/2024",
        "description": "AMAZON PAY INDIA",
        "amount": "₹1,299.00"
      }
    ]
  }
}
```

## Output Schema

| Field | Type | Description |
|-------|------|-------------|
| `issuer` | String | Bank name (HDFC/ICICI/AXIS/CHASE/IDFC) |
| `card_last_4_digits` | String\|null | Last 4 digits of card number |
| `billing_period` | String\|null | Statement period |
| `payment_due_date` | String\|null | Payment deadline |
| `total_amount_due` | String\|null | Total amount with currency symbol |
| `transactions` | Array | List of transactions with date, description, amount |

## Limitations

- **Text-based PDFs only** - No OCR for scanned documents
- **Format-specific** - Parsers match specific bank statement layouts
- **Limited banks** - Currently supports 5 banks
- **No categorization** - Returns raw transaction data

## Production Deployment

```bash
# Using Gunicorn
pip install gunicorn
cd backend
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## License

MIT License

## Author

**virti1331** - [GitHub](https://github.com/virti1331/cc-statement-parser)

# Invoice Verifier - GST Compliance System

A comprehensive web application for verifying Indian GST invoices with automated compliance checking, GSTIN validation, and duplicate detection.

## Features

### 🔍 **Invoice Verification**
- **PDF Upload & OCR**: Upload PDF invoices for automatic text extraction and field parsing
- **Manual Entry**: Input invoice details manually for verification
- **GSTIN Validation**: Complete GSTIN structure validation with checksum verification
- **Rule 46 Compliance**: Invoice number format validation per GST rules
- **Arithmetic Checks**: Tax calculations and total amount verification
- **Duplicate Detection**: Local database storage for duplicate invoice detection

### 🎯 **Validation Checks**
- **GSTIN Structure**: 15-character format, state code, PAN structure, checksum
- **Invoice Format**: Character limits, allowed characters per GST Rule 46
- **Date Parsing**: Financial year determination (India: Apr-Mar)
- **Place of Supply**: Consistency with GSTIN state code
- **HSN Code**: Format validation (4-8 digits)
- **Tax Calculations**: CGST/SGST/IGST rate and amount verification

### 🎨 **Modern Web Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Drag & Drop**: Easy PDF file upload with visual feedback
- **Real-time Results**: Instant verification with detailed breakdown
- **Visual Scoring**: Color-coded results and progress bars
- **Interactive Forms**: Enhanced user experience with validation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
uvicorn app:app --reload --port 8000
```

### 3. Open in Browser

Navigate to `http://localhost:8000` to access the web interface.

## API Endpoints

### Web Interface
- `GET /` - Main invoice verification interface
- `GET /health` - Health check endpoint

### Verification APIs
- `POST /verify` - Verify PDF invoice with file upload
- `POST /verify-json` - Verify invoice using JSON data

## Usage Examples

### 1. PDF Upload Verification

1. Open the web interface
2. Drag and drop a PDF invoice or click to browse
3. Optionally check "Store for duplicate detection"
4. Click "Verify Invoice"
5. View detailed results and compliance score

### 2. Manual Entry Verification

1. Fill in the required fields (GSTIN, Invoice Number, Date)
2. Add optional fields for comprehensive validation
3. Click "Verify Manual Entry"
4. Review validation results

### 3. API Usage (cURL)

#### Verify PDF File
```bash
curl -F "file=@invoice.pdf" -F "record=true" http://localhost:8000/verify
```

#### Verify JSON Data
```bash
curl -X POST http://localhost:8000/verify-json \
  -H 'Content-Type: application/json' \
  -d '{
    "vendor_gstin": "09AABCU6223H2ZB",
    "invoice_no": "GDDAIJEB25001819",
    "invoice_date": "25 Jun 2025",
    "place_of_supply": "Uttar Pradesh",
    "hsn": "996412",
    "taxable_value": "₹133.29",
    "cgst_rate": 2.5,
    "cgst_amount": "₹3.33",
    "sgst_rate": 2.5,
    "sgst_amount": "₹3.33",
    "total": "₹139.95"
  }'
```

## Technical Details

### Backend Architecture
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLite**: Lightweight database for duplicate detection
- **PDF Processing**: pdfminer.six for text extraction
- **Date Parsing**: python-dateutil for flexible date handling

### Frontend Technologies
- **HTML5**: Semantic markup with modern features
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: No framework dependencies
- **Font Awesome**: Icon library for visual elements

### Validation Logic
- **GSTIN Algorithm**: Weighted checksum calculation with base-36 encoding
- **State Codes**: Complete mapping of Indian state codes
- **Pattern Matching**: Regex-based field extraction from PDF text
- **Mathematical Verification**: Tax calculation validation with tolerance

## Database Schema

```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_gstin TEXT,
    invoice_no_norm TEXT,
    fy TEXT,
    original_invoice_no TEXT,
    invoice_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vendor_gstin, invoice_no_norm, fy)
);
```

## Configuration

### Environment Variables
- `INVOICE_DB`: Database file path (default: `./invoice_verifier.sqlite`)

### File Size Limits
- Maximum PDF size: 10MB (configurable in FastAPI settings)

## Development

### Project Structure
```
Marketplace/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   └── index.html       # Main web interface
├── static/               # Static assets
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend JavaScript
└── invoice_verifier.sqlite  # SQLite database (auto-created)
```

### Adding New Validation Rules
1. Extend the `verify_invoice_core` function in `app.py`
2. Add new check logic with appropriate scoring
3. Update the weights dictionary for scoring
4. Test with sample invoices

### Extending Field Extraction
1. Add new patterns to `FIELD_PATTERNS` dictionary
2. Update `extract_fields_from_text` function
3. Modify the frontend to display new fields

## Testing

### Sample Invoices
The system includes sample data for testing:
- Valid GSTIN: `09AABCU6223H2ZB`
- Valid invoice format: `GDDAIJEB25001819`
- Date format: `25 Jun 2025`

### Validation Scenarios
- **Pass**: Complete, valid invoice data
- **Review**: Minor issues or missing fields
- **Fail**: Major validation failures

## Security Notes

- **Offline Validation**: All checks are performed locally without external API calls
- **File Handling**: PDF files are processed in memory and not stored permanently
- **Input Validation**: All user inputs are validated and sanitized
- **Database**: SQLite database with proper constraints and unique keys

## Limitations

- **PDF Only**: Currently supports PDF files (image support planned)
- **English Text**: Optimized for English invoice text
- **India GST**: Specifically designed for Indian GST compliance
- **Local Storage**: Duplicate detection limited to local database

## Future Enhancements

- [ ] Image (JPG/PNG) support with OCR
- [ ] QR code scanning for e-invoices
- [ ] Government portal integration
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] API rate limiting and authentication
- [ ] Cloud database integration

## Support

For issues, questions, or contributions:
1. Check the existing documentation
2. Review the code comments in `app.py`
3. Test with sample data
4. Submit detailed bug reports

## License

This project is open source and available under the MIT License.

---

**Note**: This system performs offline validation and does not verify invoice authenticity with government portals. For legal compliance, always cross-reference with official sources.

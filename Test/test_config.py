#!/usr/bin/env python3
"""
Test Configuration for Invoice Verifier System
Contains sample test data and configuration settings
"""

# Test Configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "max_file_size": 10 * 1024 * 1024,  # 10MB
}

# Sample Valid Invoice Data
VALID_INVOICE_DATA = {
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
}

# Sample Invalid Invoice Data
INVALID_INVOICE_DATA = {
    "vendor_gstin": "09AABCU6223H2Z",  # Missing last character
    "invoice_no": "INV-12345678901234567",  # Too long
    "invoice_date": "32 Feb 2025",  # Invalid date
    "place_of_supply": "Maharashtra",  # Different from GSTIN state
    "hsn": "ABC123",  # Contains letters
    "taxable_value": "₹100.00",
    "cgst_rate": 5.0,
    "cgst_amount": "₹10.00",  # Incorrect calculation
    "total": "₹110.00"
}

# Sample Partial Invoice Data
PARTIAL_INVOICE_DATA = {
    "vendor_gstin": "27AABFU6223H2ZB",  # Maharashtra GSTIN
    "invoice_no": "INV-001",
    "invoice_date": "15 Mar 2025",
    # Missing most fields
}

# Expected Results for Valid Invoice
EXPECTED_VALID_RESULTS = {
    "verdict": "PASS",
    "score": 100,
    "checks": [
        {"name": "GSTIN Structure", "status": "PASS"},
        {"name": "Invoice Number Format", "status": "PASS"},
        {"name": "Invoice Date", "status": "PASS"},
        {"name": "Place of Supply Consistency", "status": "PASS"},
        {"name": "HSN Format", "status": "PASS"},
        {"name": "Arithmetic Checks", "status": "PASS"},
        {"name": "Duplicate Check (Local)", "status": "PASS"}
    ]
}

# Expected Results for Invalid Invoice
EXPECTED_INVALID_RESULTS = {
    "verdict": "FAIL",
    "score": 0,
    "checks": [
        {"name": "GSTIN Structure", "status": "FAIL"},
        {"name": "Invoice Number Format", "status": "FAIL"},
        {"name": "Invoice Date", "status": "FAIL"},
        {"name": "HSN Format", "status": "FAIL"},
        {"name": "Arithmetic Checks", "status": "FAIL"}
    ]
}

# Test GSTINs for Validation
TEST_GSTINS = {
    "valid": [
        "09AABCU6223H2ZB",  # Uttar Pradesh
        "27AABFU6223H2ZB",  # Maharashtra
        "33AABFU6223H2ZB",  # Tamil Nadu
        "36AABFU6223H2ZB",  # Telangana
    ],
    "invalid": [
        "09AABCU6223H2Z",   # Too short
        "09AABCU6223H2ZBA", # Too long
        "09AABCU6223H2Z1",  # Invalid checksum
        "09AABCU6223H2Z@",  # Invalid character
        "09AABCU6223H2Z ",  # Space at end
    ]
}

# Test Invoice Numbers
TEST_INVOICE_NUMBERS = {
    "valid": [
        "INV-001",
        "INV001",
        "INV/001",
        "GDDAIJEB25001819",
        "ABC123DEF456",
        "INV-2025-001"
    ],
    "invalid": [
        "INV-12345678901234567",  # Too long (>16 chars)
        "INV@001",                # Invalid character
        "INV 001",                # Space
        "INV_001",                # Underscore
        "",                       # Empty
    ]
}

# Test Dates
TEST_DATES = {
    "valid": [
        "25 Jun 2025",
        "15 Mar 2025",
        "1 Apr 2025",
        "31 Mar 2025",
        "2025-06-25",
        "25/06/2025",
        "25-06-2025"
    ],
    "invalid": [
        "32 Feb 2025",    # Invalid day
        "29 Feb 2025",    # Not leap year
        "15 13 2025",     # Invalid month
        "15 Jun 2025",    # Future date (if current year < 2025)
        "invalid date",   # Text
        "",               # Empty
    ]
}

# Test HSN Codes
TEST_HSN_CODES = {
    "valid": [
        "996412",     # 6 digits
        "9964",       # 4 digits
        "99641234",   # 8 digits
        "1234",       # 4 digits
        "99999999"    # 8 digits
    ],
    "invalid": [
        "ABC123",     # Contains letters
        "123",        # Too short (<4)
        "123456789",  # Too long (>8)
        "12.34",      # Contains decimal
        "12-34",      # Contains hyphen
        "",           # Empty
    ]
}

# Test Amounts
TEST_AMOUNTS = {
    "valid": [
        "₹100.00",
        "100.00",
        "₹1,000.50",
        "1000.50",
        "₹1,00,000.00",
        "100000.00"
    ],
    "invalid": [
        "₹100.00.00",  # Multiple decimals
        "₹100,00",     # Invalid comma placement
        "₹100.00₹",    # Multiple currency symbols
        "100.00₹",     # Currency symbol at end
        "₹100.00.00",  # Multiple decimals
        "",            # Empty
    ]
}

# Validation Rules
VALIDATION_RULES = {
    "gstin": {
        "length": 15,
        "pattern": r"^[0-9A-Z]{15}$",
        "state_codes": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                       "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                       "21", "22", "23", "24", "27", "29", "30", "32", "33", "36", "37"]
    },
    "invoice_number": {
        "max_length": 16,
        "pattern": r"^[A-Za-z0-9\-/]{1,16}$"
    },
    "hsn_code": {
        "min_length": 4,
        "max_length": 8,
        "pattern": r"^[0-9]{4,8}$"
    },
    "amount": {
        "pattern": r"^[₹Rs\.\s]*[0-9,]+\.?[0-9]*$"
    }
}

# Performance Benchmarks
PERFORMANCE_BENCHMARKS = {
    "response_time": {
        "excellent": "< 100ms",
        "good": "100-500ms",
        "fair": "500ms-1s",
        "poor": "> 1s"
    },
    "file_size": {
        "max_pdf": "10MB",
        "max_image": "5MB"
    },
    "concurrent_users": {
        "recommended": "10",
        "maximum": "50"
    }
}

# Error Messages
ERROR_MESSAGES = {
    "gstin_invalid": "GSTIN must be 15 alphanumeric characters",
    "gstin_checksum": "GSTIN checksum validation failed",
    "invoice_too_long": "Invoice number exceeds 16 characters",
    "invoice_invalid_chars": "Invoice number contains invalid characters",
    "date_invalid": "Could not parse invoice date",
    "hsn_invalid": "HSN code must be 4-8 digits",
    "amount_invalid": "Invalid amount format",
    "file_too_large": "File size exceeds maximum limit",
    "file_type_unsupported": "File type not supported",
    "server_error": "Internal server error occurred"
}

# Success Messages
SUCCESS_MESSAGES = {
    "verification_passed": "Invoice verification completed successfully",
    "verification_review": "Invoice verification completed with warnings",
    "fields_extracted": "All invoice fields extracted successfully",
    "duplicate_check": "No duplicate invoice found",
    "validation_passed": "All validation checks passed"
}

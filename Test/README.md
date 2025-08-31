# 🧪 Test Suite for Invoice Verifier System

This folder contains comprehensive testing tools and scripts for the Invoice Verifier system.

## 📁 Test Files

- **`test_config.py`** - Test configuration and sample data
- **`test_runner.py`** - Comprehensive test runner script
- **`demo.py`** - Interactive demo script
- **`run.py`** - Application startup script
- **`sample_invoice.txt`** - Sample invoice data for testing
- **`requirements.txt`** - Test-specific dependencies
- **`PROJECT_SUMMARY.md`** - Complete project documentation

## 🚀 Quick Start

### 1. Install Test Dependencies
```bash
cd test
pip install -r requirements.txt
```

### 2. Start the Application
```bash
# From the test folder
python3 run.py

# OR from the main folder
python3 -m uvicorn app:app --reload --port 8000
```

### 3. Run Tests
```bash
# Run comprehensive test suite
python3 test_runner.py

# Run interactive demo
python3 demo.py
```

## 🧪 Test Categories

### **API Testing**
- Health endpoint verification
- Web interface loading
- Static file serving
- JSON validation endpoints

### **Validation Testing**
- GSTIN structure validation
- Invoice number format checking
- Date parsing and financial year
- HSN code validation
- Tax calculation verification

### **Performance Testing**
- Response time measurement
- Load handling
- Error handling
- Edge case validation

### **Data Testing**
- Valid invoice data
- Invalid invoice data
- Partial invoice data
- Boundary conditions

## 📊 Test Results

The test runner provides:
- ✅ **Pass/Fail Status** for each test
- 📊 **Success Rate** calculation
- ⏱️ **Performance Metrics** (response times)
- 📄 **Detailed Results** saved to JSON files
- 🔍 **Error Details** for failed tests

## 🎯 Sample Test Data

### **Valid Invoice (Expected: PASS)**
```json
{
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
```

### **Invalid Invoice (Expected: FAIL)**
```json
{
  "vendor_gstin": "09AABCU6223H2Z",
  "invoice_no": "INV-12345678901234567",
  "invoice_date": "32 Feb 2025",
  "place_of_supply": "Maharashtra",
  "hsn": "ABC123",
  "taxable_value": "₹100.00",
  "cgst_rate": 5.0,
  "cgst_amount": "₹10.00",
  "total": "₹110.00"
}
```

## 🔧 Test Configuration

### **Environment Variables**
- `base_url`: Server URL (default: http://localhost:8000)
- `timeout`: Request timeout in seconds (default: 30)
- `max_file_size`: Maximum file size for testing (default: 10MB)

### **Validation Rules**
- **GSTIN**: 15 characters, alphanumeric, valid checksum
- **Invoice Number**: ≤16 characters, A-Z, 0-9, -, /
- **HSN Code**: 4-8 digits
- **Amounts**: Currency symbols, commas, decimals

## 📈 Performance Benchmarks

### **Response Time Targets**
- **Excellent**: < 100ms
- **Good**: 100-500ms
- **Fair**: 500ms-1s
- **Poor**: > 1s

### **File Size Limits**
- **PDF**: Maximum 10MB
- **Image**: Maximum 5MB

### **Concurrent Users**
- **Recommended**: 10 users
- **Maximum**: 50 users

## 🐛 Troubleshooting

### **Common Issues**

1. **Connection Refused**
   - Ensure the application is running on port 8000
   - Check firewall settings

2. **Import Errors**
   - Install test requirements: `pip install -r requirements.txt`
   - Check Python path and virtual environment

3. **Test Failures**
   - Review error messages in test output
   - Check application logs
   - Verify test data format

### **Debug Mode**
```bash
# Run with verbose output
python3 test_runner.py --verbose

# Run specific test categories
python3 test_runner.py --category api
python3 test_runner.py --category validation
```

## 🔄 Continuous Testing

### **Automated Testing**
```bash
# Run tests every 5 minutes
watch -n 300 python3 test_runner.py

# Run tests on file changes
nodemon --exec python3 test_runner.py
```

### **Integration with CI/CD**
```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    cd test
    python3 test_runner.py
```

## 📚 Advanced Testing

### **Custom Test Cases**
Add new test data to `test_config.py`:
```python
CUSTOM_TEST_DATA = {
    "vendor_gstin": "27AABFU6223H2ZB",
    "invoice_no": "CUSTOM-001",
    "invoice_date": "1 Apr 2025"
}
```

### **Performance Testing**
```bash
# Run benchmark tests
python3 -m pytest test_performance.py --benchmark-only

# Generate performance report
python3 -m pytest test_performance.py --benchmark-json=results.json
```

### **Coverage Testing**
```bash
# Run with coverage
python3 -m pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🎉 Success Criteria

Tests are considered successful when:
- ✅ **100% API endpoints** respond correctly
- ✅ **All validation rules** work as expected
- ✅ **Performance targets** are met
- ✅ **Error handling** works properly
- ✅ **Edge cases** are handled gracefully

## 📞 Support

For testing issues:
1. Check the test output for error details
2. Verify the application is running correctly
3. Review the test configuration
4. Check system resources and network connectivity

---

**🎯 Ready to test your Invoice Verifier system thoroughly!**

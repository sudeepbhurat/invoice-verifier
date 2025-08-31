#!/usr/bin/env python3
"""
Comprehensive Test Runner for Invoice Verifier System
Tests all aspects of the system including API endpoints, validation logic, and edge cases
"""

import requests
import json
import time
import sys
from datetime import datetime
from test_config import *

class InvoiceVerifierTester:
    def __init__(self):
        self.base_url = TEST_CONFIG["base_url"]
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_details": []
        }
        self.session = requests.Session()
        self.session.timeout = TEST_CONFIG["timeout"]

    def print_header(self, title):
        print("\n" + "="*80)
        print(f" {title}")
        print("="*80)

    def print_test_result(self, test_name, status, message="", details=None):
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
        if details:
            print(f"    Details: {details}")
        
        # Record test result
        self.results["total_tests"] += 1
        if status == "PASS":
            self.results["passed"] += 1
        elif status == "FAIL":
            self.results["failed"] += 1
        else:
            self.results["errors"] += 1
        
        self.results["test_details"].append({
            "name": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        self.print_header("Testing Health Endpoint")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") == True:
                    self.print_test_result("Health Check", "PASS", "Server is healthy")
                else:
                    self.print_test_result("Health Check", "FAIL", "Health check returned unexpected data")
            else:
                self.print_test_result("Health Check", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Health Check", "FAIL", f"Connection error: {str(e)}")

    def test_web_interface(self):
        """Test the main web interface"""
        self.print_header("Testing Web Interface")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                if "Invoice Verifier" in response.text:
                    self.print_test_result("Web Interface", "PASS", "Main page loads successfully")
                else:
                    self.print_test_result("Web Interface", "FAIL", "Page content not as expected")
            else:
                self.print_test_result("Web Interface", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Web Interface", "FAIL", f"Connection error: {str(e)}")

    def test_static_files(self):
        """Test static file serving"""
        self.print_header("Testing Static Files")
        
        static_files = [
            "/static/css/style.css",
            "/static/js/app.js"
        ]
        
        for file_path in static_files:
            try:
                response = self.session.get(f"{self.base_url}{file_path}")
                if response.status_code == 200:
                    self.print_test_result(f"Static File: {file_path}", "PASS", "File served successfully")
                else:
                    self.print_test_result(f"Static File: {file_path}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test_result(f"Static File: {file_path}", "FAIL", f"Connection error: {str(e)}")

    def test_valid_invoice_verification(self):
        """Test verification with valid invoice data"""
        self.print_header("Testing Valid Invoice Verification")
        
        try:
            response = self.session.post(
                f"{self.base_url}/verify-json",
                json=VALID_INVOICE_DATA,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("verdict") == "PASS" and data.get("score") == 100:
                    self.print_test_result("Valid Invoice", "PASS", "Verification passed with 100% score")
                else:
                    self.print_test_result("Valid Invoice", "FAIL", 
                                        f"Expected PASS, got {data.get('verdict')} with score {data.get('score')}")
            else:
                self.print_test_result("Valid Invoice", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Valid Invoice", "FAIL", f"Request error: {str(e)}")

    def test_invalid_invoice_verification(self):
        """Test verification with invalid invoice data"""
        self.print_header("Testing Invalid Invoice Verification")
        
        try:
            response = self.session.post(
                f"{self.base_url}/verify-json",
                json=INVALID_INVOICE_DATA,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("verdict") == "FAIL" and data.get("score") == 0:
                    self.print_test_result("Invalid Invoice", "PASS", "Verification correctly failed with 0% score")
                else:
                    self.print_test_result("Invalid Invoice", "FAIL", 
                                        f"Expected FAIL, got {data.get('verdict')} with score {data.get('score')}")
            else:
                self.print_test_result("Invalid Invoice", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Invalid Invoice", "FAIL", f"Request error: {str(e)}")

    def test_partial_invoice_verification(self):
        """Test verification with partial invoice data"""
        self.print_header("Testing Partial Invoice Verification")
        
        try:
            response = self.session.post(
                f"{self.base_url}/verify-json",
                json=PARTIAL_INVOICE_DATA,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("verdict") in ["FAIL", "REVIEW"]:
                    self.print_test_result("Partial Invoice", "PASS", 
                                        f"Verification correctly handled partial data: {data.get('verdict')}")
                else:
                    self.print_test_result("Partial Invoice", "FAIL", 
                                        f"Expected FAIL/REVIEW, got {data.get('verdict')}")
            else:
                self.print_test_result("Partial Invoice", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Partial Invoice", "FAIL", f"Request error: {str(e)}")

    def test_gstin_validation(self):
        """Test GSTIN validation with various inputs"""
        self.print_header("Testing GSTIN Validation")
        
        # Test valid GSTINs
        for gstin in TEST_GSTINS["valid"]:
            test_data = {"vendor_gstin": gstin, "invoice_no": "TEST001", "invoice_date": "25 Jun 2025"}
            try:
                response = self.session.post(
                    f"{self.base_url}/verify-json",
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if GSTIN validation passed
                    gstin_check = next((check for check in data.get("checks", []) 
                                      if check.get("name") == "GSTIN Structure"), None)
                    
                    if gstin_check and gstin_check.get("status") == "PASS":
                        self.print_test_result(f"GSTIN: {gstin}", "PASS", "Valid GSTIN accepted")
                    else:
                        self.print_test_result(f"GSTIN: {gstin}", "FAIL", "Valid GSTIN rejected")
                else:
                    self.print_test_result(f"GSTIN: {gstin}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test_result(f"GSTIN: {gstin}", "FAIL", f"Request error: {str(e)}")

    def test_invoice_number_validation(self):
        """Test invoice number validation"""
        self.print_header("Testing Invoice Number Validation")
        
        # Test valid invoice numbers
        for inv_no in TEST_INVOICE_NUMBERS["valid"]:
            test_data = {"vendor_gstin": "09AABCU6223H2ZB", "invoice_no": inv_no, "invoice_date": "25 Jun 2025"}
            try:
                response = self.session.post(
                    f"{self.base_url}/verify-json",
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    inv_check = next((check for check in data.get("checks", []) 
                                   if check.get("name") == "Invoice Number Format"), None)
                    
                    if inv_check and inv_check.get("status") == "PASS":
                        self.print_test_result(f"Invoice Number: {inv_no}", "PASS", "Valid format accepted")
                    else:
                        self.print_test_result(f"Invoice Number: {inv_no}", "FAIL", "Valid format rejected")
                else:
                    self.print_test_result(f"Invoice Number: {inv_no}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test_result(f"Invoice Number: {inv_no}", "FAIL", f"Request error: {str(e)}")

    def test_performance(self):
        """Test system performance"""
        self.print_header("Testing System Performance")
        
        # Test response time
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/verify-json",
                json=VALID_INVOICE_DATA,
                headers={'Content-Type': 'application/json'}
            )
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                if response_time < 100:
                    self.print_test_result("Response Time", "PASS", f"Excellent: {response_time:.2f}ms")
                elif response_time < 500:
                    self.print_test_result("Response Time", "PASS", f"Good: {response_time:.2f}ms")
                elif response_time < 1000:
                    self.print_test_result("Response Time", "PASS", f"Fair: {response_time:.2f}ms")
                else:
                    self.print_test_result("Response Time", "FAIL", f"Poor: {response_time:.2f}ms")
            else:
                self.print_test_result("Response Time", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Response Time", "FAIL", f"Request error: {str(e)}")

    def test_error_handling(self):
        """Test error handling"""
        self.print_header("Testing Error Handling")
        
        # Test with malformed JSON
        try:
            response = self.session.post(
                f"{self.base_url}/verify-json",
                data="invalid json",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 422:  # Validation error
                self.print_test_result("Malformed JSON", "PASS", "Properly handled invalid JSON")
            else:
                self.print_test_result("Malformed JSON", "FAIL", f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.print_test_result("Malformed JSON", "FAIL", f"Request error: {str(e)}")

        # Test with missing required fields
        try:
            response = self.session.post(
                f"{self.base_url}/verify-json",
                json={},  # Empty data
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("verdict") == "FAIL":
                    self.print_test_result("Missing Fields", "PASS", "Properly handled missing data")
                else:
                    self.print_test_result("Missing Fields", "FAIL", "Did not handle missing data correctly")
            else:
                self.print_test_result("Missing Fields", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test_result("Missing Fields", "FAIL", f"Request error: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Invoice Verifier Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_web_interface()
        self.test_static_files()
        self.test_valid_invoice_verification()
        self.test_invalid_invoice_verification()
        self.test_partial_invoice_verification()
        self.test_gstin_validation()
        self.test_invoice_number_validation()
        self.test_performance()
        self.test_error_handling()
        
        # Print summary
        self.print_header("Test Summary")
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️ Errors: {self.results['errors']}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['failed'] == 0 and self.results['errors'] == 0:
            print("\n🎉 All tests passed! System is working correctly.")
        else:
            print(f"\n⚠️ {self.results['failed'] + self.results['errors']} tests failed. Check the details above.")
        
        # Save detailed results
        self.save_test_results()
        
        return self.results['failed'] == 0 and self.results['errors'] == 0

    def save_test_results(self):
        """Save detailed test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📄 Detailed results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {str(e)}")

def main():
    """Main function to run tests"""
    tester = InvoiceVerifierTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

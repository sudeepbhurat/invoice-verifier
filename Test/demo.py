#!/usr/bin/env python3
"""
Invoice Verifier Demo Script
This script demonstrates the invoice verification system with sample data
"""

import requests
import json
import time

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(result):
    print(f"\n🎯 Verdict: {result['verdict']}")
    print(f"📊 Score: {result['score']}/100")
    
    print("\n📋 Validation Checks:")
    for check in result['checks']:
        status_icon = {
            'PASS': '✅',
            'WARN': '⚠️',
            'FAIL': '❌',
            'INFO': 'ℹ️'
        }.get(check['status'], '❓')
        
        print(f"  {status_icon} {check['name']}: {check['message']}")
        
        if check['data']:
            print(f"     Data: {json.dumps(check['data'], indent=6)}")

def demo_valid_invoice():
    """Demo with a valid invoice"""
    print_separator("DEMO 1: Valid Invoice (Expected: PASS)")
    
    data = {
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
    
    print("📄 Sample Invoice Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    try:
        response = requests.post(
            'http://localhost:8000/verify-json',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(result)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure the application is running.")
        print("   Run: python3 -m uvicorn app:app --reload --port 8000")

def demo_invalid_invoice():
    """Demo with an invalid invoice"""
    print_separator("DEMO 2: Invalid Invoice (Expected: FAIL)")
    
    data = {
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
    
    print("📄 Sample Invoice Data (with issues):")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    try:
        response = requests.post(
            'http://localhost:8000/verify-json',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(result)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure the application is running.")
        print("   Run: python3 -m uvicorn app:app --reload --port 8000")

def demo_partial_invoice():
    """Demo with partial invoice data"""
    print_separator("DEMO 3: Partial Invoice (Expected: REVIEW)")
    
    data = {
        "vendor_gstin": "27AABFU6223H2ZB",  # Maharashtra GSTIN
        "invoice_no": "INV-001",
        "invoice_date": "15 Mar 2025",
        # Missing most fields
    }
    
    print("📄 Sample Invoice Data (partial):")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    try:
        response = requests.post(
            'http://localhost:8000/verify-json',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(result)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure the application is running.")
        print("   Run: python3 -m uvicorn app:app --reload --port 8000")

def main():
    """Run all demos"""
    print("🚀 Invoice Verifier System Demo")
    print("This script demonstrates the invoice verification capabilities")
    print("Make sure the application is running on http://localhost:8000")
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Run demos
    demo_valid_invoice()
    demo_invalid_invoice()
    demo_partial_invoice()
    
    print_separator("DEMO COMPLETE")
    print("🎉 All demonstrations completed!")
    print("\n💡 Key Features Demonstrated:")
    print("  ✅ GSTIN structure and checksum validation")
    print("  ✅ Invoice number format compliance (Rule 46)")
    print("  ✅ Date parsing and financial year determination")
    print("  ✅ Place of supply consistency checking")
    print("  ✅ HSN code format validation")
    print("  ✅ Tax calculation verification")
    print("  ✅ Comprehensive scoring system")
    print("\n🌐 Open http://localhost:8000 in your browser for the web interface")

if __name__ == "__main__":
    main()

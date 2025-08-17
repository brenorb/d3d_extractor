#!/usr/bin/env python3
"""
Simple test script for the Diabetes3D API
"""
import os
from pathlib import Path

import requests

API_BASE = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_process_pdf():
    """Test PDF processing with a sample file"""
    print("\n📄 Testing PDF processing...")
    
    # Look for a test PDF file
    data_dir = Path("data")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in data/ directory")
        return False
    
    test_file = pdf_files[0]
    print(f"Using test file: {test_file}")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "application/pdf")}
            response = requests.post(f"{API_BASE}/process-lab-results", files=files)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Processing successful!")
            print(f"Filename: {result.get('filename')}")
            print(f"Pages processed: {result.get('pages_processed')}")
            print(f"Processing time: {result.get('processing_time')}s")
            print(f"Results keys: {list(result.get('results', {}).keys())}")
            return True
        else:
            print(f"❌ Processing failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API tests...\n")
    
    # Test health endpoint
    health_ok = test_health()
    
    if not health_ok:
        print("❌ Health check failed, skipping other tests")
        return
    
    # Test PDF processing (only if we have a .env file with API key)
    if os.path.exists(".env") or os.getenv("OPENROUTER_API_KEY"):
        test_process_pdf()
    else:
        print("\n⚠️  No .env file or OPENROUTER_API_KEY found")
        print("   Skipping PDF processing test")
        print("   Create .env file with OPENROUTER_API_KEY to test full pipeline")
    
    print("\n✅ API tests completed!")
    print(f"📖 Visit {API_BASE}/docs for interactive API documentation")

if __name__ == "__main__":
    main()

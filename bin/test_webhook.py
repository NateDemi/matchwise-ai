#!/usr/bin/env python3
"""
Test script to demonstrate webhook usage
"""

import requests
import json

def test_webhook():
    """Test the webhook service"""
    
    # Webhook service URL (adjust as needed)
    webhook_url = "http://localhost:5000/webhook/process-receipts"
    
    # Test payload
    payload = {
        "docupanda_id": "test123",
        "vendor_name": "Walmart",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    print(f"🚀 Testing webhook at: {webhook_url}")
    print(f"📤 Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(webhook_url, json=payload)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the webhook service is running.")
        print("💡 Start it with: python bin/webhook_service.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health_check():
    """Test the health check endpoint"""
    
    health_url = "http://localhost:5000/health"
    
    print(f"\n🏥 Testing health check at: {health_url}")
    
    try:
        response = requests.get(health_url)
        print(f"📥 Health Status: {response.status_code}")
        print(f"📥 Health Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed! Service not running.")

if __name__ == "__main__":
    print("🧪 Webhook Testing Suite")
    print("=" * 40)
    
    test_health_check()
    test_webhook()

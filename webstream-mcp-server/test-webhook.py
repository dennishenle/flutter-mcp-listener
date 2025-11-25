#!/usr/bin/env python3
"""
Test script for the WebhookMCP Server
Tests webhook registration and message pushing
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_webhook_registration():
    """Test registering a webhook"""
    print("🧪 Testing webhook registration...")
    
    test_webhook_url = "http://localhost:3000/webhook"
    
    response = requests.post(
        f"{BASE_URL}/api/register",
        json={"webhook_url": test_webhook_url},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Webhook registered: {data}")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        return False

def test_list_webhooks():
    """Test listing registered webhooks"""
    print("\n🧪 Testing webhook listing...")
    
    response = requests.get(f"{BASE_URL}/api/webhooks")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Webhooks listed: {data}")
        return True
    else:
        print(f"❌ Listing failed: {response.status_code} - {response.text}")
        return False

def test_push_message():
    """Test pushing a message to webhooks"""
    print("\n🧪 Testing message push...")
    
    response = requests.post(
        f"{BASE_URL}/api/push",
        json={"message": "Test message from webhook test script!"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Message pushed: {data}")
        return True
    else:
        print(f"❌ Push failed: {response.status_code} - {response.text}")
        return False

def test_unregister_webhook():
    """Test unregistering a webhook"""
    print("\n🧪 Testing webhook unregistration...")
    
    test_webhook_url = "http://localhost:3000/webhook"
    
    response = requests.post(
        f"{BASE_URL}/api/unregister",
        json={"webhook_url": test_webhook_url},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Webhook unregistered: {data}")
        return True
    else:
        print(f"❌ Unregistration failed: {response.status_code} - {response.text}")
        return False

def main():
    print("=" * 60)
    print("WebhookMCP Server Test Suite")
    print("=" * 60)
    
    # Check if server is accessible
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print(f"✅ Server is accessible at {BASE_URL}\n")
        else:
            print(f"⚠️ Server returned status {response.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"Error: {e}")
        print("\nMake sure the server is running:")
        print("  docker-compose up -d")
        return
    
    # Run tests
    results = []
    
    results.append(("Register webhook", test_webhook_registration()))
    time.sleep(0.5)
    
    results.append(("List webhooks", test_list_webhooks()))
    time.sleep(0.5)
    
    results.append(("Push message", test_push_message()))
    time.sleep(0.5)
    
    results.append(("Unregister webhook", test_unregister_webhook()))
    time.sleep(0.5)
    
    results.append(("List webhooks (after unregister)", test_list_webhooks()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()


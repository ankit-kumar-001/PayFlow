import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_transactions():
    print("Testing transaction simulation flow...")
    
    unique_email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup & Login
    requests.post(f"{BASE_URL}/auth/signup", json={
        "email": unique_email,
        "password": password,
        "full_name": "Test Transactor"
    })
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email, "password": password})
    token = resp.json().get("access_token")
    
    # 2. Create Merchant
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/merchants", json={"business_name": "Txn Business"}, headers=headers)
    merchant = resp.json()
    api_key, api_secret = merchant["api_key"], merchant["api_secret"]
    merchant_headers = {"X-API-Key": api_key, "X-API-Secret": api_secret}
    
    # 3. Create a link
    resp = requests.post(f"{BASE_URL}/payment-links", json={"amount": 50, "currency": "USD"}, headers=merchant_headers)
    link1_id = resp.json()["id"]
    
    # 4. Pay link 1 (success)
    resp = requests.post(f"{BASE_URL}/payment-links/{link1_id}/pay", json={
        "payment_method": "card",
        "simulate_failure": False
    })
    assert resp.status_code == 201, f"Failed to pay link 1: {resp.text}"
    txn1 = resp.json()
    assert txn1["status"] == "success"
    print("  [OK] Paid link 1 successfully")
    
    # 5. Get the transaction using merchant credentials
    resp = requests.get(f"{BASE_URL}/transactions/{txn1['id']}", headers=merchant_headers)
    assert resp.status_code == 200, f"Failed to fetch transaction: {resp.text}"
    assert resp.json()["id"] == txn1["id"]
    print("  [OK] Fetched transaction by ID")
    
    # 6. Pay link 1 again (should fail with 409)
    resp = requests.post(f"{BASE_URL}/payment-links/{link1_id}/pay", json={
        "payment_method": "upi",
        "simulate_failure": False
    })
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}: {resp.text}"
    print("  [OK] Duplicate payment properly rejected")
    
    # 7. Create another link
    resp = requests.post(f"{BASE_URL}/payment-links", json={"amount": 25.5, "currency": "USD"}, headers=merchant_headers)
    link2_id = resp.json()["id"]
    
    # 8. Pay link 2 with failure
    resp = requests.post(f"{BASE_URL}/payment-links/{link2_id}/pay", json={
        "payment_method": "netbanking",
        "simulate_failure": True
    })
    assert resp.status_code == 201, f"Failed to pay link 2: {resp.text}"
    txn2 = resp.json()
    assert txn2["status"] == "failed"
    print("  [OK] Paid link 2 with simulate_failure=True")
    
    print("\nAll transaction tests passed successfully!")

if __name__ == "__main__":
    try:
        test_transactions()
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)

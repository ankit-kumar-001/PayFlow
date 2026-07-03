import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_payment_links():
    print("Testing payment links flow...")
    
    unique_email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup
    signup_data = {
        "email": unique_email,
        "password": password,
        "full_name": "Test Merchant User"
    }
    resp = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    assert resp.status_code == 200, f"Signup failed: {resp.text}"
    
    # 2. Login
    login_data = {"email": unique_email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json().get("access_token")
    
    # 3. Create Merchant
    headers = {"Authorization": f"Bearer {token}"}
    merchant_data = {"business_name": "Test Business"}
    resp = requests.post(f"{BASE_URL}/merchants", json=merchant_data, headers=headers)
    assert resp.status_code == 201, f"Create merchant failed: {resp.text}"
    merchant = resp.json()
    api_key = merchant["api_key"]
    api_secret = merchant["api_secret"]
    
    print(f"  [OK] Merchant created: {merchant['id']}")
    
    # 4. Create Payment Link
    merchant_headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret
    }
    link_data = {
        "amount": 100.50,
        "currency": "USD",
        "description": "Test Payment Link"
    }
    resp = requests.post(f"{BASE_URL}/payment-links", json=link_data, headers=merchant_headers)
    assert resp.status_code == 201, f"Create payment link failed: {resp.text}"
    link = resp.json()
    link_id = link["id"]
    
    print(f"  [OK] Payment link created: {link_id}")
    
    # 5. Fetch Publicly
    resp = requests.get(f"{BASE_URL}/payment-links/{link_id}")
    assert resp.status_code == 200, f"Fetch payment link failed: {resp.text}"
    fetched_link = resp.json()
    assert fetched_link["id"] == link_id
    assert fetched_link["amount"] == "100.50"
    
    print(f"  [OK] Payment link fetched publicly")
    
    # 6. List Payment Links
    resp = requests.get(f"{BASE_URL}/payment-links", headers=merchant_headers)
    assert resp.status_code == 200, f"List payment links failed: {resp.text}"
    links = resp.json()
    assert len(links) > 0
    assert any(l["id"] == link_id for l in links)
    
    print(f"  [OK] Payment links listed successfully")

if __name__ == "__main__":
    try:
        test_payment_links()
        print("\nAll payment link tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)

import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_cache():
    print("Testing Redis Cache Flow...")
    
    unique_email = f"test_cache_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup & Login
    requests.post(f"{BASE_URL}/auth/signup", json={
        "email": unique_email,
        "password": password,
        "full_name": "Test Cacher"
    })
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email, "password": password})
    token = resp.json().get("access_token")
    
    # 2. Create Merchant
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/merchants", json={"business_name": "Cache Business"}, headers=headers)
    merchant = resp.json()
    merchant_headers = {"X-API-Key": merchant["api_key"], "X-API-Secret": merchant["api_secret"]}
    
    # 3. Create a link
    resp = requests.post(f"{BASE_URL}/payment-links", json={"amount": 100, "currency": "USD"}, headers=merchant_headers)
    link_id = resp.json()["id"]
    print(f"Created link {link_id}")
    
    # 4. Fetch link (Miss -> cache populated)
    print("Fetching first time...")
    resp = requests.get(f"{BASE_URL}/payment-links/{link_id}", headers=merchant_headers)
    assert resp.status_code == 200
    
    # 5. Fetch link again (Hit -> from cache)
    print("Fetching second time (should be cache hit, check server logs)...")
    resp = requests.get(f"{BASE_URL}/payment-links/{link_id}", headers=merchant_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "created"
    
    # 6. Pay link
    print("Paying the link...")
    resp = requests.post(f"{BASE_URL}/payment-links/{link_id}/pay", json={
        "payment_method": "card",
        "simulate_failure": False
    })
    assert resp.status_code == 201
    
    # 7. Fetch link again (Miss -> Cache invalidated)
    print("Fetching third time after pay (status should be paid)...")
    resp = requests.get(f"{BASE_URL}/payment-links/{link_id}", headers=merchant_headers)
    assert resp.status_code == 200
    status = resp.json()["status"]
    print(f"Status is now: {status}")
    assert status == "paid", f"Status should be paid, got {status}"
    
    print("\nCache testing passed!")

if __name__ == "__main__":
    try:
        test_cache()
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)

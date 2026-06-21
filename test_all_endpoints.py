import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    print("  [OK] /health")

def test_signup_and_login():
    print("Testing /auth/signup and /auth/login...")
    unique_email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Signup
    signup_data = {
        "email": unique_email,
        "password": password,
        "full_name": "Test User"
    }
    resp = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    assert resp.status_code == 200, f"Expected 200 for signup, got {resp.status_code}: {resp.text}"
    print("  [OK] Signup successful")
    
    # 2. Duplicate Signup
    resp = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    assert resp.status_code == 400, f"Expected 400 for duplicate signup, got {resp.status_code}: {resp.text}"
    print("  [OK] Duplicate signup properly rejected")
    
    # 3. Login
    login_data = {"email": unique_email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert resp.status_code == 200, f"Expected 200 for login, got {resp.status_code}: {resp.text}"
    token = resp.json().get("access_token")
    assert token is not None, "Token not found in response"
    print("  [OK] Login successful")
    
    # 4. Invalid Login
    invalid_login_data = {"email": unique_email, "password": "wrongpassword"}
    resp = requests.post(f"{BASE_URL}/auth/login", json=invalid_login_data)
    assert resp.status_code == 401, f"Expected 401 for invalid login, got {resp.status_code}: {resp.text}"
    print("  [OK] Invalid login properly rejected")
    
    return token

def test_auth_me(token):
    print("Testing /auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Valid token
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert resp.status_code == 200, f"Expected 200 for /auth/me, got {resp.status_code}: {resp.text}"
    print("  [OK] /auth/me successful")
    
    # 2. Invalid token
    invalid_headers = {"Authorization": f"Bearer {token}invalid"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=invalid_headers)
    assert resp.status_code == 401, f"Expected 401 for invalid token, got {resp.status_code}: {resp.text}"
    print("  [OK] Invalid token properly rejected")

if __name__ == "__main__":
    try:
        test_health()
        token = test_signup_and_login()
        test_auth_me(token)
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)

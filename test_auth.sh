#!/bin/bash
set -e

echo "=== Testing Signup ==="
curl -s -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test2@example.com", "password": "password123", "full_name": "Test User 2"}' | jq

echo -e "\n=== Testing Login ==="
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test2@example.com", "password": "password123"}')

echo $RESPONSE | jq

TOKEN=$(echo $RESPONSE | jq -r .access_token)

echo -e "\n=== Testing /auth/me ==="
curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq

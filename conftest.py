import pytest
import requests

BASE_URL = "http://localhost:8080"

@pytest.fixture(scope="session")
def auth_token():
    """整个测试会话共用同一个Token"""
    url = f"{BASE_URL}/login"
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    token = response.json()["token"]
    print(f"\n获取到Token: {token[:20]}...")
    return token
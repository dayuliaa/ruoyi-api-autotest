import requests

# 若依后端地址
BASE_URL = "http://localhost:8080"


# 1. 测试登录成功
def test_login_success():
    url = f"{BASE_URL}/login"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(url, json=payload)
    print("登录响应状态码:", response.status_code)
    print("登录响应内容:", response.text)

    # 断言：状态码200，返回数据中有token
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["code"] == 200
    assert "token" in json_data


# 2. 测试登录失败（密码错误）
def test_login_fail_wrong_password():
    url = f"{BASE_URL}/login"
    payload = {
        "username": "admin",
        "password": "wrongpassword"
    }
    response = requests.post(url, json=payload)
    print("错误密码登录响应:", response.text)

    # 断言：code 应该是 500（若依默认逻辑）
    json_data = response.json()
    assert json_data["code"] == 500
    assert "token" not in json_data
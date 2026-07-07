import requests
import time

BASE_URL = "http://localhost:8080"


def test_get_user_list(auth_token):
    url = f"{BASE_URL}/system/user/list"
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"pageNum": 1, "pageSize": 10}

    response = requests.get(url, headers=headers, params=params)
    print(response)
    print("用户列表响应:", response.status_code)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["code"] == 200
    assert "rows" in json_data
    assert isinstance(json_data["rows"], list)

def test_get_user_list_without_token():
    """测试不带Token直接请求用户列表，应该被拒绝"""
    url = f"{BASE_URL}/system/user/list"

    # 注意：这里故意不传 headers，也就是不传 Token
    response = requests.get(url)

    print("不带Token的响应状态码:", response.status_code)
    print("不带Token的响应内容:", response.text)

    # 若依在未登录时访问接口，会返回 500 并提示"缺失令牌"
    assert response.status_code == 200  # HTTP层面通常还是200
    json_data = response.json()
    assert json_data["code"] == 401  # 业务层面是失败
    assert "令牌" in json_data["msg"] or "认证" in json_data["msg"]

def test_get_user_list_real(auth_token):
    url = f"{BASE_URL}/system/user/list"
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"pageNum": 1, "pageSize": 1}

    response = requests.get(url, headers=headers, params=params)
    print(response.text)
    print("用户列表响应:", response.status_code)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["code"] == 200
    assert isinstance(json_data["rows"], list)
    assert json_data["total"] >= 2
    assert len(json_data["rows"]) == 1


def test_update_user(auth_token):
    """测试修改用户昵称，然后查列表验证修改成功"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 第一步：从用户列表里随便取一个用户，拿到他的userId
    list_url = f"{BASE_URL}/system/user/list"
    list_response = requests.get(list_url, headers=headers)
    users = list_response.json()["rows"]
    target_user = users[1]  # 取第一个用户
    user_id = target_user["userId"]
    old_nickname = target_user["nickName"]

    # 第二步：修改这个用户的昵称
    update_url = f"{BASE_URL}/system/user"
    new_nickname = "修改后的昵称_" + str(user_id)
    payload = {
        "userId": user_id,
        "nickName": new_nickname,
        "userName": target_user["userName"],
        "deptId": target_user["deptId"],
        "email": target_user["email"],
        "phonenumber": target_user["phonenumber"],
        "sex": target_user["sex"],
        "status": target_user["status"]
    }

    update_response = requests.put(update_url, headers=headers, json=payload)
    print("修改用户响应:", update_response.text)
    assert update_response.json()["code"] == 200

    # 第三步：查列表验证昵称真的变了
    verify_response = requests.get(list_url, headers=headers, params={"userName": target_user["userName"]})
    updated_nickname = verify_response.json()["rows"][0]["nickName"]
    assert updated_nickname == new_nickname
    print(f"昵称从 '{old_nickname}' 改为 '{updated_nickname}'，修改成功")


def test_update_user_without_token():
    """测试不带Token修改用户，应该被拒绝"""
    url = f"{BASE_URL}/system/user"
    payload = {"userId": 1, "nickName": "黑客"}

    response = requests.put(url, json=payload)
    print("不带Token修改用户响应:", response.text)

    assert response.json()["code"] == 401
    assert "认证失败" in response.json()["msg"]


def test_delete_user(auth_token):
    """测试新建一个用户，再删除，最后查列表验证删除成功"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 第一步：新建一个临时用户，准备删除
    create_url = f"{BASE_URL}/system/user"
    temp_username = "temp_delete_test"
    payload = {
        "userName": temp_username,
        "nickName": "待删除用户",
        "password": "123456",
        "deptId": 105,
        "phonenumber": "13900000001",
        "email": "temp@test.com",
        "sex": "1",
        "status": "0"
    }
    create_response = requests.post(create_url, headers=headers, json=payload)
    print("创建待删除用户响应:", create_response.text)
    assert create_response.json()["code"] == 200

    # 第二步：查列表拿到这个新用户的userId
    list_url = f"{BASE_URL}/system/user/list"
    list_response = requests.get(list_url, headers=headers, params={"userName": temp_username})
    user_id = list_response.json()["rows"][0]["userId"]
    print(f"待删除用户ID: {user_id}")

    # 第三步：删除这个用户
    delete_url = f"{BASE_URL}/system/user/{user_id}"
    delete_response = requests.delete(delete_url, headers=headers)
    print("删除用户响应:", delete_response.text)
    assert delete_response.json()["code"] == 200

    # 第四步：查列表验证用户已经不存在了
    verify_response = requests.get(list_url, headers=headers, params={"userName": temp_username})
    total = verify_response.json()["total"]
    assert total == 0
    print(f"用户 {temp_username} 已删除，列表查询结果total={total}")


def test_delete_user_not_exist(auth_token):
    """测试删除不存在的用户，应该返回错误"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    url = f"{BASE_URL}/system/user/99999"

    response = requests.delete(url, headers=headers)
    print("删除不存在用户响应:", response.text)

    assert response.json()["code"] == 500

def test_get_user_list_by_status_active(auth_token):
    """测试按状态筛选：只查启用的用户，验证返回的都是status=0"""
    url = f"{BASE_URL}/system/user/list"
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"status": "0"}  # ← 关键：加了这个参数

    response = requests.get(url, headers=headers, params=params)
    print("按状态筛选响应:", response.text)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["code"] == 200
    assert json_data["total"] >= 1

    for user in json_data["rows"]:
        assert user["status"] == "0"

def test_create_user_invalid_phone(auth_token):
    """测试新增用户时手机号格式错误，应该被拒绝"""
    url = f"{BASE_URL}/system/user"
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "userName": "test_wrong_phone",   # 自己定义一个唯一的用户名
        "nickName": "手机号错误用户",
        "password": "123456",
        "deptId": 105,
        "phonenumber": "abc123",           # 故意传非法手机号
        "email": "test@test.com",
        "sex": "1",
        "status": "0"
    }

    response = requests.post(url, headers=headers, json=payload)
    print("手机号错误响应:", response.text)

    assert response.status_code == 200  # ✅ HTTP层面成功
    json_data = response.json()
    assert json_data["code"] == 500  # ✅ 业务层面失败（手机号格式错误）
    msg = json_data["msg"]
    assert ("手机" in msg) or ("格式" in msg)
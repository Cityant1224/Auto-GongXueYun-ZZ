import json, time, requests
from modules.crypto import aes_encrypt, aes_decrypt
from modules.headers import header_user_agent


def get_token(user):
    url = "https://api.moguding.net:9000/session/user/v5/login"
    data = {
        "phone": aes_encrypt(user["phone"]),
        "password": aes_encrypt(user["password"]),
        "captcha": None,
        "loginType": "android",
        "uuid": "",
        "device": "android",
        "version": "5.14.0",
        "t": aes_encrypt(str(int(time.time() * 1000))),
    }
    headers = {
        "content-type": "application/json; charset=UTF-8",
        "user-agent": header_user_agent(user),
    }
    try:
        res = requests.post(url=url, data=json.dumps(data), headers=headers)
        if res.status_code == 200:
            encrypted_data = res.json().get("data", "")
            decrypted_data = aes_decrypt(encrypted_data)
            user_info = json.loads(decrypted_data)
            # 打印请求登录并且解密后的响应, 包含了重要信息, 比如userId和token
            # print(user_info)
            return {"code": 200, "data": user_info}
        else:
            return {
                "code": res.status_code,
                "msg": f"请求失败, 状态码: {res.status_code}",
            }
    except Exception as e:
        print(f"请求失败, 发生异常: {e}")
        return {"code": -1, "msg": str(e)}

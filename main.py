from datetime import datetime, timezone, timedelta
import json
import os
import random
import time
from hashlib import md5


import requests
from utils import AES, UTC as pytz

import MessagePush

pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep

# 设置重连次数
requests.adapters.DEFAULT_RETRIES = 5

# 设置GMT+7时区
gmt_use_time = timezone(timedelta(hours=8))

# 获取GMT+7时间并判断是上班还是下班
gmt_time = datetime.now(gmt_use_time)
is_start = gmt_time.hour < 12


def get_plan_id(user, token: str, sign: str):
    url = "https://api.moguding.net:9000/practice/plan/v3/getPlanByStu"
    data = {"state": ""}
    headers2 = {
        "roleKey": "student",
        "authorization": token,
        "sign": sign,
        "content-type": "application/json; charset=UTF-8",
        "user-agent": getUserAgent(user),
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()["data"][0]["planId"]


def getUserAgent(user):
    if user["user-agent"] != "null":
        return user["user-agent"]
    user["user-agent"] = random.choice(
        [
            "Mozilla/5.0 (Linux; U; Android 9; zh-cn; Redmi Note 5 Build/PKQ1.180904.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.10.8",
            "Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.3 (Baidu; P1 9)",
            "Mozilla/5.0 (Linux; Android 10; EVR-AL00 Build/HUAWEIEVR-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 baiduboxapp/11.0.5.12 (Baidu; P1 10)",
            "Mozilla/5.0 (Linux; Android 9; JKM-AL00b Build/HUAWEIJKM-AL00b; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045130 Mobile Safari/537.36 MMWEBID/8951 MicroMessenger/7.0.12.1620(0x27000C36) Process/tools NetType/4G Language/zh_CN ABI/arm64",
            "Mozilla/5.0 (Linux; Android 8.1.0; PBAM00 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0) NABar/2.0",
            "Mozilla/5.0 (Linux; Android 10; LIO-AN00 Build/HUAWEILIO-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 XWEB/1170 MMWEBSDK/200201 Mobile Safari/537.36 MMWEBID/3371 MicroMessenger/7.0.12.1620(0x27000C36) Process/toolsmp NetType/4G Language/zh_CN ABI/arm64",
        ]
    )
    return user["user-agent"]


def getSign2(text: str):
    s = text + "3478cbbc33f84bd00d75d7dfa69e0daa"
    return md5(s.encode("utf-8")).hexdigest()


def parseUserInfo():
    allUser = ""
    if os.path.exists(pwd + "user.json"):
        print("找到配置文件,将从配置文件读取信息！")
        with open(pwd + "user.json", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                allUser = allUser + line + "\n"
    else:
        return json.loads(os.environ.get("USERS", ""))
    return json.loads(allUser)


def save(
    user,
    userId,
    token,
    planId,
    country,
    province,
    address,
    signType="START",
    device="Android",
    latitude=None,
    longitude=None,
):
    text = device + signType + planId + userId + address
    headers2 = {
        "roleKey": "student",
        "user-agent": getUserAgent(user),
        "sign": getSign2(text=text),
        "authorization": token,
        "content-type": "application/json; charset=UTF-8",
    }
    data = {
        "country": country,
        "address": address,
        "province": province,
        "city": user["city"],
        "area": user["area"],
        "latitude": latitude,
        "description": user["desc"],
        "planId": planId,
        "type": signType,
        "device": device,
        "longitude": longitude,
    }
    url = "https://api.moguding.net:9000/attendence/clock/v2/save"
    res = requests.post(url=url, headers=headers2, data=json.dumps(data))

    # 检查响应是否为有效的 JSON 格式
    try:
        response_json = res.json()
    except json.JSONDecodeError:
        print(f"服务器返回了无效的 JSON 响应: {res.text}")
        return False, "服务器返回了无效的 JSON 响应"

    # 检查响应中是否包含 'code' 键
    if "code" not in response_json:
        print(f"服务器响应中没有 'code' 键: {response_json}")
        return False, "服务器响应中没有 'code' 键"

    # 正常处理响应
    return response_json["code"] == 200, response_json["msg"]


def encrypt(key, text):
    aes = AES(key.encode("utf-8"))
    res = aes.encrypt(text.encode("utf-8"))
    msg = res.hex()
    return msg


def getToken(user):
    url = "https://api.moguding.net:9000/session/user/v3/login"
    t = str(int(time.time() * 1000))
    data = {
        "password": encrypt("23DbtQHR2UMbH6mJ", user["password"]),
        "phone": encrypt("23DbtQHR2UMbH6mJ", user["phone"]),
        "t": encrypt("23DbtQHR2UMbH6mJ", t),
        "loginType": user["type"],
        "uuid": "",
    }
    headers2 = {
        "content-type": "application/json; charset=UTF-8",
        "user-agent": getUserAgent(user),
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()


def useUserTokenSign(user):
    phone = user["phone"]
    token = user["token"]
    userId = user["userId"]
    planId = user["planId"]
    signStatus = startSign(userId, token, planId, user, startType=0)
    if signStatus:
        print("警告：保持登录失败，Token失效，请及时更新Token")
        print("重试：正在准备使用账户密码重新签到")
        MessagePush.pushMessage(
            phone,
            "工学云设备Token失效",
            "工学云自动打卡设备Token失效，本次将使用账号密码重新登录签到，请及时更新配置文件中的Token"
            + ",如不再需要保持登录状态,请及时将配置文件中的keepLogin更改为False取消保持登录打卡，如有疑问请联系邮箱：XuanRanDev@qq.com",
            user["pushKey"],
        )
        prepareSign(user, keepLogin=False)


def prepareSign(user, keepLogin=True):
    if not user["enable"]:
        return

    if user["keepLogin"] and keepLogin:
        # 启用了保持登录状态，则使用设备Token登录
        print("用户启用了保持登录，准备使用设备Token登录")
        useUserTokenSign(user)
        return

    userInfo = getToken(user)
    phone = user["phone"]

    if userInfo["code"] != 200:
        print("打卡失败，错误原因:" + userInfo["msg"])
        MessagePush.pushMessage(
            phone,
            "工学云打卡失败！",
            "用户: " + phone + "," + "打卡失败！错误原因：" + userInfo["msg"],
            user["pushKey"],
        )
        return

    userId = userInfo["data"]["userId"]
    token = userInfo["data"]["token"]

    sign = getSign2(userId + "student")
    planId = get_plan_id(user, token, sign)
    startSign(userId, token, planId, user, startType=1)


# startType = 0 使用保持登录状态签到
# startType = 1 使用登录签到
def startSign(userId, token, planId, user, startType):
    hourNow = datetime.datetime.now(pytz.timezone("PRC")).hour
    if hourNow < 12:
        signType = "START"
    else:
        signType = "END"
    phone = user["phone"]
    print("-------------准备签到--------------")

    latitude = user["latitude"]
    longitude = user["longitude"]
    if user["randomLocation"]:
        latitude = latitude[0 : len(latitude) - 1] + str(random.randint(0, 10))
        longitude = longitude[0 : len(longitude) - 1] + str(random.randint(0, 10))

    signResp, msg = save(
        user,
        userId,
        token,
        planId,
        user["country"],
        user["province"],
        user["address"],
        signType=signType,
        device=user["type"],
        latitude=latitude,
        longitude=longitude,
    )
    if signResp:
        print("签到成功")
    else:
        print("签到失败")
        if not startType:
            print("-------------签到完成--------------")
            return True

    ######################################
    # 处理推送信息
    pushSignType = "上班"
    if signType == "END":
        pushSignType = "下班"

    pushSignIsOK = "成功！"
    if not signResp:
        pushSignIsOK = "失败！"

    signStatus = "打卡"

    hourNow = datetime.datetime.now(pytz.timezone("PRC")).hour
    if hourNow == 11 or hourNow == 23:
        signStatus = "补签"

    # 推送消息内容构建

    MessagePush.pushMessage(
        phone,
        "工学云" + pushSignType + signStatus + pushSignIsOK,
        "用户：" + phone + "，工学云" + pushSignType + signStatus + pushSignIsOK,
        user["pushKey"],
    )

    # 消息推送处理完毕
    #####################################

    print("-------------签到完成--------------")


def signCheck(users):
    for user in users:
        if not user["signCheck"] and user["enable"]:
            continue

        print()
        url = "https://api.moguding.net:9000/attendence/clock/v1/listSynchro"
        if user["keepLogin"]:
            print("          此用户保持登录状态开启，准备使用Token查询          ")
            token = user["token"]
        else:
            print("            此用户保持登录状态关闭，准备登录账号          ")
            token = getToken(user)["data"]["token"]
        header = {
            "accept-encoding": "gzip",
            "content-type": "application/json;charset=UTF-8",
            "rolekey": "student",
            "host": "api.moguding.net:9000",
            "authorization": token,
            "user-agent": getUserAgent(user),
        }
        t = str(int(time.time() * 1000))
        data = {"t": encrypt("23DbtQHR2UMbH6mJ", t)}
        res = requests.post(url=url, headers=header, data=json.dumps(data))

        if res.json()["msg"] != "success":
            print("            获取用户打卡记录失败          ")
            continue

        lastSignInfo = res.json()["data"][0]
        lastSignDate = lastSignInfo["dateYmd"]
        lastSignType = lastSignInfo["type"]
        hourNow = datetime.datetime.now(pytz.timezone("PRC")).hour
        nowDate = str(datetime.datetime.now(pytz.timezone("PRC")))[0:10]
        if hourNow <= 12 and lastSignType == "END" and lastSignDate != nowDate:
            print("            今日未打上班卡，准备补签          ")
            prepareSign(user)
        if hourNow >= 23 and lastSignType == "START" and lastSignDate == nowDate:
            print("            今日未打下班卡，准备补签          ")
            prepareSign(user)
        print("        Tips：如果没提示上班或者下班补签即代表上次打卡正常          ")
        continue


def prepareSign(users):
    # 初始化打卡成功和失败的数量
    success_count = 0
    fail_count = 0

    # 用来存储推送消息的字典，key为pushKey，value为消息内容
    push_messages = {}

    for user in users:
        if not user["enable"]:
            continue

        userInfo = getToken(user)
        phone = user["phone"]
        remark = user.get("remark", "")  # 从配置文件中读取remark值

        user_info_prefix = f"[{remark}/{phone}]"

        if userInfo["code"] != 200:
            print(f"{user_info_prefix}打卡失败，错误原因: {userInfo['msg']}")
            fail_count += 1
            continue

        userId = userInfo["data"]["userId"]
        token = userInfo["data"]["token"]
        sign = getSign2(userId + "student")
        planId = get_plan_id(user, token, sign)

        # 使用上海时间判断是上班还是下班
        signType = "START" if is_start else "END"
        print(f"{user_info_prefix}准备{signType}打卡")

        signResp, msg = save(
            user,
            userId,
            token,
            planId,
            user["country"],
            user["province"],
            user["address"],
            signType=signType,
            device=user["type"],
            latitude=user["latitude"],
            longitude=user["longitude"],
        )

        # 推送消息内容构建
        pushSignType = "上班" if signType == "START" else "下班"
        pushSignIsOK = "成功！" if signResp else "失败！"
        signStatus = "打卡"

        hourNow = gmt_time.hour
        if hourNow == 11 or hourNow == 23:
            signStatus = "补签"

        push_message = (
            f"{user_info_prefix}工学云{pushSignType}{signStatus}{pushSignIsOK}\n"
        )
        push_messages.setdefault(user["pushKey"], []).append(push_message)
        # 判断打卡是否成功并更新计数
        if signResp:
            success_count += 1
        else:
            fail_count += 1

    # 合并同pushKey的消息并推送
    for pushKey, messages in push_messages.items():
        # 找到所有具有相同pushKey的用户
        users_with_same_pushkey = [user for user in users if user["pushKey"] == pushKey]
        title = "工学云打卡通知"
        content = "".join(messages)
        content += f"\n打卡时间: {gmt_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"成功数量: [{success_count}/{len(users)}]\n失败数量: [{fail_count}/{len(users)}]"
        MessagePush.pushMessage(users_with_same_pushkey, title, content, pushKey)


if __name__ == "__main__":
    users = parseUserInfo()
    prepareSign(users)

import logging
import os
import uuid
from datetime import datetime

import requests

API_BASE = "https://api.kurobbs.com"
USER_MINE_URL = f"{API_BASE}/user/mineV2"
FIND_ROLE_LIST_URL = f"{API_BASE}/gamer/role/default"
SIGN_URL = f"{API_BASE}/encourage/signIn/v2"
USER_SIGN_URL = f"{API_BASE}/user/signIn"
SMS_CODE_URL = f"{API_BASE}/user/getSmsCode"
SDK_LOGIN_URL = f"{API_BASE}/user/sdkLogin"

GAME_NAME_MAP = {2: "战双帕弥什", 3: "鸣潮"}

token_save_name = "KURO_TOKEN.txt"
token_env = os.environ.get("KURO_TOKEN")
current_type = os.environ.get("KURO_TYPE")


def get_login_headers() -> dict:
    return {
        "osversion": "Android",
        "devcode": "2fba3859fe9bfe9099f2696b8648c2c6",
        "distinct_id": str(uuid.uuid4()),
        "countrycode": "CN",
        "ip": "10.0.2.233",
        "model": "2211133C",
        "source": "android",
        "lang": "zh-Hans",
        "version": "1.0.9",
        "versioncode": "1090",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.10.0",
    }


def get_headers(token: str) -> dict:
    return {
        "osversion": "Android",
        "devcode": "2fba3859fe9bfe9099f2696b8648c2c6",
        "countrycode": "CN",
        "source": "android",
        "lang": "zh-Hans",
        "version": "1.0.9",
        "versioncode": "1090",
        "token": token,
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.10.0",
    }


def make_request(url: str, data: dict, token: str) -> dict:
    headers = get_headers(token)
    resp = requests.post(url, headers=headers, data=data)
    return resp.json()


def get_mine_info(token: str) -> dict:
    return make_request(USER_MINE_URL, {"type": 1}, token)


def get_role_list(user_id: int, token: str) -> list:
    resp = make_request(FIND_ROLE_LIST_URL, {"queryUserId": user_id}, token)
    if resp.get("code") != 200:
        return []
    return resp.get("data", {}).get("defaultRoleList", [])


def sign_community(token: str) -> str:
    resp = make_request(USER_SIGN_URL, {"gameId": 2}, token)
    if resp.get("code") == 200:
        return "库街区社区签到成功"
    return f"库街区社区签到失败: {resp.get('msg', '未知错误')}"


def sign_game(role: dict, token: str) -> str:
    game_id = role.get("gameId")
    game_name = GAME_NAME_MAP.get(game_id, f"游戏{game_id}")
    nickname = role.get("roleName", "")

    data = {
        "gameId": game_id,
        "serverId": role.get("serverId"),
        "roleId": role.get("roleId"),
        "userId": role.get("userId"),
        "reqMonth": f"{datetime.now().month:02d}",
    }
    resp = make_request(SIGN_URL, data, token)
    if resp.get("code") != 200:
        return f"[{game_name}]角色{nickname}签到失败: {resp.get('msg', '未知错误')}"
    return f"[{game_name}]角色{nickname}签到成功"


def do_sign(token: str) -> tuple:
    logs = []
    success = True

    try:
        logs.append(sign_community(token))

        mine_info = get_mine_info(token)
        user_data = mine_info.get("data", {}).get("mine", {})
        user_id = user_data.get("userId", 0)

        if user_id:
            roles = get_role_list(user_id, token)
            for role in roles:
                try:
                    logs.append(sign_game(role, token))
                except Exception as e:
                    logs.append(f"签到角色{role.get('roleName', '')}异常: {e}")
                    success = False
        else:
            logs.append("库街区: 无法获取用户ID")
            success = False

    except Exception as e:
        logs.append(f"库街区签到异常: {e}")
        success = False

    return success, logs


def send_phone_code(phone: str) -> dict:
    headers = get_login_headers()
    headers["devcode"] = "073A9EFAC18FC50616DD15808DAE719DBCB904B7"
    resp = requests.post(SMS_CODE_URL, headers=headers, data={"mobile": phone, "geeTestData": ""})
    return resp.json()


def login_by_code(phone: str, code: str) -> str:
    headers = get_login_headers()
    resp = requests.post(SDK_LOGIN_URL, headers=headers, data={
        "mobile": phone,
        "code": code,
        "devCode": "2fba3859fe9bfe9099f2696b8648c2c6",
        "gameList": "",
    }).json()
    if resp.get("code") != 200:
        raise Exception(f"库街区登录失败: {resp.get('msg', '未知错误')}")
    token = resp.get("data", {}).get("token")
    if not token:
        raise Exception("库街区登录成功但未返回 token")
    return token


def save(tokens: list):
    with open(token_save_name, "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))
    logging.info(
        f"您的库街区 token 已保存在 {token_save_name}, "
        f"打开这个文件可以把它复制到云函数/GitHub Actions 上使用!\n"
        f"下次如需添加账号，设置环境变量 KURO_TYPE=add_account 即可重新进入添加模式"
    )


def read(path: str) -> list:
    if not os.path.exists(path):
        return []
    v = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t and t not in v:
                v.append(t)
    return v


def read_from_env() -> list:
    v = []
    token_list = token_env.split(",")
    for t in token_list:
        t = t.strip()
        if t and t not in v:
            v.append(t)
    logging.info(f"从环境变量 KURO_TOKEN 读取到 {len(v)} 个库街区 token")
    return v


def init_token() -> list:
    if token_env:
        logging.info("使用环境变量里面的库街区 token")
        return read_from_env()
    tokens = []
    tokens.extend(read(token_save_name))
    add_account = current_type == "add_account"
    if add_account:
        logging.info("！！！您启用了库街区添加账号模式，将不会签到！！！")
    if len(tokens) == 0 or add_account:
        tokens.append(input_for_token())
        save(tokens)
    return [] if add_account else tokens


def input_for_token() -> str:
    print("=" * 50)
    print("获取库街区 token，请选择：")
    print("1.使用手机验证码登录（推荐）")
    print("2.手动输入已抓包获取的 token")
    print("=" * 50)
    mode = input("请输入（1，2）：").strip()
    if mode == "" or mode == "1":
        phone = input("请输入手机号码：").strip()
        resp = send_phone_code(phone)
        if resp.get("code") != 200:
            raise Exception(f"发送验证码失败: {resp.get('msg', '未知错误')}")
        if resp.get("data", {}).get("geeTest") is True:
            raise Exception("触发极验人机验证，请改用方法2手动输入 token")
        code = input("请输入手机验证码：").strip()
        return login_by_code(phone, code)
    elif mode == "2":
        print()
        print("获取 token 的方法：")
        print("  - Android: 安装库街区 APP → 登录 → 用 HttpCanary/Reqable 抓包")
        print("  - iOS: 安装库街区 APP → 登录 → 用 Stream/Thor 抓包")
        print("  抓取任意 api.kurobbs.com 域名的请求，复制请求头中 token 字段的值")
        print("  教程: https://blog.tomys.top/2023-07/kuro-token/")
        print()
        token = input("请粘贴你的库街区 token: ").strip()
        if not token:
            print("token 不能为空，已退出")
            exit(-1)
        return token
    else:
        exit(-1)


def start() -> tuple:
    tokens = init_token()
    if not tokens:
        logging.warning("库街区: 添加账号模式，跳过签到")
        return True, ["库街区: 添加账号模式，已跳过签到"]

    all_success = True
    all_logs = []

    for i, token in enumerate(tokens):
        logging.info(f"库街区: 正在签到第 {i + 1}/{len(tokens)} 个账号...")
        success, logs = do_sign(token)
        all_success = all_success and success
        all_logs.extend(logs)

    logging.info("库街区签到完成！")
    return all_success, all_logs

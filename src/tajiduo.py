import base64
import hashlib
import json
import logging
import os
import time
import uuid
from urllib import parse

import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SECRET = '89155cc4e8634ec5b1b6364013b23e3e'
APP_ID = '10550'
USER_CENTER_APP_ID = '10551'

DEVICETYPE = 'LGE-AN10'
TYPE = '16'
DEVICENAME = 'LGE-AN10'
VERSIONCODE = '1'
AREACODEID = '1'
DEVICESYS = '12'
DEVICEMODEL = 'LGE-AN10'
SDKVERSION = '4.129.0'
BID = 'com.pwrd.htassistant'
CHANNELID = '1'
APPVERSION = '1.1.0'
OKHTTP_UA = 'okhttp/4.12.0'

FORM_HEADERS = {
    'platform': 'android',
    'Content-Type': 'application/x-www-form-urlencoded',
}

SEND_CAPTCHA_URL = 'https://user.laohu.com/m/newApi/sendPhoneCaptchaWithOutLogin'
CHECK_CAPTCHA_URL = 'https://user.laohu.com/m/newApi/checkPhoneCaptchaWithOutLogin'
LOGIN_URL = 'https://user.laohu.com/openApi/sms/new/login'
PASSWORD_LOGIN_URL = 'https://user.laohu.com/m/newApi/login'
USER_CENTER_LOGIN_URL = 'https://bbs-api.tajiduo.com/usercenter/api/login'
REFRESH_TOKEN_URL = 'https://bbs-api.tajiduo.com/usercenter/api/refreshToken'
APP_SIGNIN_URL = 'https://bbs-api.tajiduo.com/apihub/api/signin'
GAME_SIGNIN_URL = 'https://bbs-api.tajiduo.com/apihub/awapi/sign'
GET_GAME_ROLES_URL = 'https://bbs-api.tajiduo.com/usercenter/api/v2/getGameRoles'

token_save_name = 'TAJIDUO_TOKEN.txt'
token_env = os.environ.get('TAJIDUO_TOKEN')
current_type = os.environ.get('TAJIDUO_TYPE')
DEFAULT_GAME_ID = '1289'


def generate_sign(params: dict) -> str:
    sorted_keys = sorted(params.keys())
    values = ''.join(str(params[k]) for k in sorted_keys)
    return hashlib.md5((values + SECRET).encode('utf-8')).hexdigest()


def aes_base64_encode(text: str) -> str:
    key = SECRET[-16:].encode('utf-8')
    padder = padding.PKCS7(128).padder()
    padded = padder.update(text.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(encrypted).decode('utf-8')


def random_device_id() -> str:
    return uuid.uuid4().hex


def _post_form(url: str, data: dict, headers: dict = None) -> requests.Response:
    return requests.post(url, data=parse.urlencode(data), headers=headers or FORM_HEADERS)


def _safe_json(response, label):
    if not response.text.strip():
        raise Exception(f'{label}: status={response.status_code}')
    try:
        return response.json()
    except json.JSONDecodeError:
        raise Exception(f'{label}: {response.text[:200]}')


def _dedup(items: list) -> list:
    result = []
    for i in items:
        if i and i not in result:
            result.append(i)
    return result


def _parse_account_line(line: str) -> dict:
    line = line.strip()
    if not line:
        return None
    try:
        raw = json.loads(line)
    except json.JSONDecodeError:
        return {
            'refreshToken': line,
            'uid': '',
            'deviceId': random_device_id(),
            'gameId': DEFAULT_GAME_ID,
        }
    if not isinstance(raw, dict):
        return None
    return {
        'refreshToken': str(raw.get('refreshToken', '')).strip(),
        'uid': str(raw.get('uid', '')).strip(),
        'deviceId': str(raw.get('deviceId', '')).strip() or random_device_id(),
        'gameId': str(raw.get('gameId', DEFAULT_GAME_ID)).strip() or DEFAULT_GAME_ID,
    }


def _account_to_line(account: dict) -> str:
    return json.dumps({
        'refreshToken': account.get('refreshToken', ''),
        'uid': account.get('uid', ''),
        'deviceId': account.get('deviceId', random_device_id()),
        'gameId': account.get('gameId', DEFAULT_GAME_ID),
    }, ensure_ascii=False)


def send_captcha(phone: str, device_id: str):
    data = {
        'deviceType': DEVICETYPE, 'type': TYPE, 'deviceId': device_id,
        'deviceName': DEVICENAME, 'versionCode': VERSIONCODE,
        't': str(int(time.time())), 'areaCodeId': AREACODEID, 'appId': APP_ID,
        'deviceSys': DEVICESYS, 'cellphone': phone, 'deviceModel': DEVICEMODEL,
        'sdkVersion': SDKVERSION, 'bid': BID, 'channelId': CHANNELID,
    }
    data['sign'] = generate_sign(data)
    resp = _safe_json(_post_form(SEND_CAPTCHA_URL, data), '发送验证码')
    if resp.get('code') != 0:
        raise Exception(f'发送验证码失败: {resp.get("message") or resp.get("msg") or resp}')


def check_captcha(phone: str, code: str, device_id: str):
    data = {
        'deviceType': DEVICETYPE, 'deviceId': device_id, 'deviceName': DEVICENAME,
        'versionCode': VERSIONCODE, 't': str(int(time.time())),
        'captcha': code, 'appId': APP_ID, 'deviceSys': DEVICESYS,
        'cellphone': phone, 'deviceModel': DEVICEMODEL,
        'sdkVersion': SDKVERSION, 'bid': BID, 'channelId': CHANNELID,
    }
    data['sign'] = generate_sign(data)
    resp = _safe_json(_post_form(CHECK_CAPTCHA_URL, data), '校验验证码')
    if resp.get('code') != 0:
        raise Exception(f'验证码错误: {resp.get("message") or resp.get("msg") or resp}')


def sms_login(phone: str, code: str, device_id: str) -> tuple:
    data = {
        'deviceType': DEVICETYPE, 'idfa': '', 'sign': '', 'adm': '',
        'type': TYPE, 'deviceId': device_id, 'version': VERSIONCODE,
        'deviceName': DEVICENAME, 'mac': '',
        't': str(int(time.time() * 1000)),
        'areaCodeId': AREACODEID,
        'captcha': aes_base64_encode(code),
        'appId': APP_ID, 'deviceSys': DEVICESYS,
        'cellphone': aes_base64_encode(phone),
        'deviceModel': DEVICEMODEL,
        'sdkVersion': SDKVERSION, 'bid': BID, 'channelId': CHANNELID,
    }
    data['sign'] = generate_sign(data)
    resp = _safe_json(_post_form(LOGIN_URL, data), '登录')
    if resp.get('code') != 0:
        raise Exception(f'登录失败: {resp.get("message") or resp.get("msg") or resp}')
    result = resp.get('result') or {}
    token = result.get('token')
    user_id = result.get('userId')
    if not token or user_id is None:
        raise Exception(f'登录返回缺少 token/userId')
    return token, str(user_id)


def password_login(phone: str, password: str, device_id: str) -> tuple:
    data = {
        'deviceType': DEVICETYPE, 'type': TYPE, 'deviceId': device_id,
        'deviceName': DEVICENAME, 'versionCode': VERSIONCODE,
        't': str(int(time.time())), 'areaCodeId': AREACODEID, 'appId': APP_ID,
        'deviceSys': DEVICESYS,
        'username': phone,
        'password': password,
        'deviceModel': DEVICEMODEL,
        'sdkVersion': SDKVERSION, 'bid': BID, 'channelId': CHANNELID,
    }
    data['sign'] = generate_sign(data)
    resp = _safe_json(_post_form(PASSWORD_LOGIN_URL, data), '密码登录')
    if resp.get('code') != 0:
        msg = str(resp.get('message') or resp.get('msg') or resp)
        if 'BAD_REQUEST' in msg:
            data['username'] = aes_base64_encode(phone)
            data['password'] = aes_base64_encode(password)
            data['sign'] = generate_sign(data)
            resp = _safe_json(_post_form(PASSWORD_LOGIN_URL, data), '密码登录(AES)')
        if resp.get('code') != 0:
            raise Exception(f'密码登录失败: {resp.get("message") or resp.get("msg") or resp}')
    result = resp.get('result') or {}
    token = result.get('token')
    user_id = result.get('userId')
    if not token or user_id is None:
        raise Exception(f'密码登录返回缺少 token/userId')
    return token, str(user_id)


def user_center_login(token: str, user_id: str, device_id: str) -> dict:
    headers = {
        **FORM_HEADERS,
        'deviceid': device_id,
        'authorization': '',
        'appversion': APPVERSION,
        'uid': '10000000',
        'User-Agent': OKHTTP_UA,
    }
    payload = {
        'token': token,
        'userIdentity': user_id,
        'appId': USER_CENTER_APP_ID,
    }
    resp = _safe_json(_post_form(USER_CENTER_LOGIN_URL, payload, headers), '用户中心登录')
    if resp.get('code') != 0:
        raise Exception(f'用户中心登录失败: {resp.get("msg") or resp}')
    data = resp.get('data') or {}
    if not data.get('accessToken') or not data.get('refreshToken'):
        raise Exception(f'用户中心登录缺少 accessToken/refreshToken')
    return data


def refresh_access_token(refresh_token_str: str, device_id: str) -> tuple:
    headers = {
        **FORM_HEADERS,
        'deviceid': device_id,
        'authorization': refresh_token_str,
        'appversion': APPVERSION,
        'uid': '10000000',
        'User-Agent': OKHTTP_UA,
    }
    resp = _safe_json(requests.post(REFRESH_TOKEN_URL, headers=headers), '刷新token')
    if resp.get('code') != 0:
        raise Exception(f'refreshToken 已失效，请重新登录: {resp.get("msg") or resp}')
    data = resp.get('data') or {}
    return data.get('accessToken', ''), data.get('refreshToken', ''), str(data.get('uid', ''))


def sign_community(access_token: str, uid: str, device_id: str) -> str:
    headers = {
        **FORM_HEADERS,
        'authorization': access_token,
        'uid': uid,
        'deviceid': device_id,
        'appversion': APPVERSION,
        'User-Agent': OKHTTP_UA,
    }
    resp = _safe_json(_post_form(APP_SIGNIN_URL, {'communityId': '1'}, headers), '社区签到')
    if resp.get('code') == 0:
        d = resp.get('data') or {}
        exp = d.get('exp', 0)
        coin = d.get('goldCoin', 0)
        return f'塔吉多社区签到成功, 获得{exp}经验, {coin}金币'
    msg = str(resp.get('msg') or resp.get('message') or resp)
    if any(k in msg for k in ['已签到', '签到过', '重复签到']):
        return '塔吉多社区签到: 今日已签到'
    return f'塔吉多社区签到失败: {msg}'


def sign_game(access_token: str, game_id: str) -> list:
    headers = {
        **FORM_HEADERS,
        'authorization': access_token,
        'appversion': APPVERSION,
        'User-Agent': OKHTTP_UA,
    }
    gc_headers = {
        'platform': 'android',
        'authorization': access_token,
        'uid': '10000000',
        'deviceid': random_device_id(),
        'appversion': APPVERSION,
        'User-Agent': OKHTTP_UA,
    }
    roles_resp = _safe_json(
        requests.get(GET_GAME_ROLES_URL, headers=gc_headers, params={'gameId': game_id}),
        f'获取角色(gameId={game_id})'
    )
    results = []
    if roles_resp.get('code') != 0:
        return [f'塔吉多获取角色失败: {roles_resp.get("msg")}']
    roles = (roles_resp.get('data') or {}).get('roles', [])
    for role in roles:
        rid = str(role.get('roleId', ''))
        rname = role.get('roleName', '')
        gname = role.get('gameName', f'游戏{game_id}')
        sname = role.get('serverName', '')
        resp = _safe_json(
            _post_form(GAME_SIGNIN_URL, {'roleId': rid, 'gameId': game_id}, headers),
            f'游戏签到(gameId={game_id})'
        )
        if resp.get('code') == 0:
            results.append(f'[{gname}]角色{rname}({sname}): 签到成功')
        else:
            msg = str(resp.get('msg') or resp.get('message') or resp)
            if any(k in msg for k in ['已签到', '签到过', '重复签到']):
                results.append(f'[{gname}]角色{rname}({sname}): 今日已签到')
            else:
                results.append(f'[{gname}]角色{rname}({sname}): 签到失败 - {msg}')
    return results


def do_sign(account: dict) -> tuple:
    logs = []
    success = True
    try:
        refresh_token_str = account['refreshToken']
        device_id = account.get('deviceId') or random_device_id()
        uid = account.get('uid', '')
        game_id = account.get('gameId', DEFAULT_GAME_ID)

        access_token, new_refresh, new_uid = refresh_access_token(refresh_token_str, device_id)
        if new_refresh:
            account['refreshToken'] = new_refresh
        if new_uid:
            account['uid'] = new_uid
            uid = new_uid

        logs.append(sign_community(access_token, uid, device_id))

        for gid in _dedup([game_id, DEFAULT_GAME_ID, '1289', '1257']):
            logs.extend(sign_game(access_token, gid))

    except Exception as e:
        logs.append(f'塔吉多签到异常: {e}')
        success = False

    return success, logs


def save(accounts: list):
    with open(token_save_name, 'w', encoding='utf-8') as f:
        f.write('\n'.join(_account_to_line(a) for a in accounts))
    logging.info(
        f'塔吉多账号已保存在 {token_save_name}, '
        f'下次如需添加账号，设置环境变量 TAJIDUO_TYPE=add_account 即可'
    )


def read(path: str) -> list:
    if not os.path.exists(path):
        return []
    accounts = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            account = _parse_account_line(line)
            if account:
                accounts.append(account)
    return accounts


def read_from_env() -> list:
    accounts = []
    rows = [r.strip() for r in token_env.replace('\n', ',').split(',') if r.strip()]
    for row in rows:
        account = _parse_account_line(row)
        if account:
            accounts.append(account)
    logging.info(f'从环境变量 TAJIDUO_TOKEN 读取到 {len(accounts)} 个塔吉多账号')
    return accounts


def init_token() -> list:
    if token_env:
        logging.info('使用环境变量里面的塔吉多 token')
        return read_from_env()
    accounts = []
    accounts.extend(read(token_save_name))
    add_account = current_type == 'add_account'
    if add_account:
        logging.info('！！！您启用了塔吉多添加账号模式，将不会签到！！！')
    if len(accounts) == 0 or add_account:
        accounts.append(input_for_token())
        save(accounts)
    return [] if add_account else accounts


def input_for_token() -> dict:
    print('=' * 50)
    print('塔吉多 登录方式:')
    print('  1. 手机号 + 密码登录（推荐）')
    print('  2. 手机号 + 验证码登录')
    print('  3. 手动输入 refreshToken（高级）')
    print('=' * 50)
    mode = input('请输入 (1/2/3): ').strip()

    if mode == '3':
        token = input('请输入 refreshToken: ').strip()
        if not token:
            exit(-1)
        uid = input('可选: 输入 uid (留空跳过): ').strip()
        game_id = input('可选: 输入 gameId (留空默认1289): ').strip() or DEFAULT_GAME_ID
        return {
            'refreshToken': token,
            'uid': uid,
            'deviceId': random_device_id(),
            'gameId': game_id,
        }

    phone = input('请输入手机号: ').strip()
    device_id = random_device_id()

    try:
        if mode == '2':
            send_captcha(phone, device_id)
            code = input('请输入验证码: ').strip()
            check_captcha(phone, code, device_id)
            token, uid = sms_login(phone, code, device_id)
        else:
            password = input('请输入密码 (不会回显): ').strip()
            token, uid = password_login(phone, password, device_id)

        uc = user_center_login(token, uid, device_id)
        logging.info(f'塔吉多登录成功, uid={uc.get("uid")}')

        return {
            'refreshToken': uc['refreshToken'],
            'uid': str(uc.get('uid', uid)),
            'deviceId': device_id,
            'gameId': DEFAULT_GAME_ID,
        }
    except Exception as e:
        logging.error(f'塔吉多登录失败: {e}')
        raise


def start() -> tuple:
    tokens = init_token()
    if not tokens:
        logging.warning('塔吉多: 添加账号模式，跳过签到')
        return True, ['塔吉多: 添加账号模式，已跳过签到']

    all_success = True
    all_logs = []

    for i, account in enumerate(tokens):
        logging.info(f'塔吉多: 正在签到第 {i + 1}/{len(tokens)} 个账号...')
        success, logs = do_sign(account)
        all_success = all_success and success
        all_logs.extend(logs)

    logging.info('塔吉多签到完成！')
    return all_success, all_logs

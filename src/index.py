import logging
import threading

import skyland
import kurobbs

file_save_skyland_token = './code/INPUT_HYPERGRYPH_TOKEN.txt'
file_save_kuro_token = './code/INPUT_KURO_TOKEN.txt'
file_save_tajiduo_token = './code/INPUT_TAJIDUO_TOKEN.txt'

logging.getLogger().setLevel(logging.INFO)


def read(path):
    v = []
    with open(path, 'r', encoding='utf-8') as f:
        for i in f.readlines():
            i = i.strip()
            i and i not in v and v.append(i)
    return v


def read_tajiduo(path):
    import json
    accounts = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                raw = {'refreshToken': line, 'uid': '', 'deviceId': '', 'gameId': '1289'}
            if isinstance(raw, dict):
                accounts.append({
                    'refreshToken': str(raw.get('refreshToken', '')).strip(),
                    'uid': str(raw.get('uid', '')).strip(),
                    'deviceId': str(raw.get('deviceId', '')).strip(),
                    'gameId': str(raw.get('gameId', '1289')).strip() or '1289',
                })
    return accounts


def handler():
    threads = []

    skyland_tokens = read(file_save_skyland_token)
    if skyland_tokens:
        logging.info(f'读取到 {len(skyland_tokens)} 个森空岛账号')
        for token in skyland_tokens:
            t = threading.Thread(target=skyland_sign, args=(token,))
            t.start()
            threads.append(t)

    kuro_tokens = read(file_save_kuro_token)
    if kuro_tokens:
        logging.info(f'读取到 {len(kuro_tokens)} 个库街区账号')
        for token in kuro_tokens:
            t = threading.Thread(target=kuro_sign, args=(token,))
            t.start()
            threads.append(t)

    import os
    if os.path.exists(file_save_tajiduo_token):
        tajiduo_accounts = read_tajiduo(file_save_tajiduo_token)
        if tajiduo_accounts:
            logging.info(f'读取到 {len(tajiduo_accounts)} 个塔吉多账号')
            for account in tajiduo_accounts:
                t = threading.Thread(target=tajiduo_sign, args=(account,))
                t.start()
                threads.append(t)

    for t in threads:
        t.join()

    logging.info('全部签到完成')


def skyland_sign(token):
    try:
        cred = skyland.get_cred_by_token(token)
        skyland.do_sign(cred)
    except Exception as ex:
        logging.error('森空岛签到失败：', exc_info=ex)


def kuro_sign(token):
    try:
        kurobbs.do_sign(token)
    except Exception as ex:
        logging.error('库街区签到失败：', exc_info=ex)


def tajiduo_sign(account):
    try:
        import tajiduo
        tajiduo.do_sign(account)
    except Exception as ex:
        logging.error('塔吉多签到失败：', exc_info=ex)


handler()

import logging
import os
import threading

import nte

# 华为云本地文件在./code下面
token_files = [
    './code/INPUT_TAJIDUO_TOKEN.txt',
    './code/INPUT_HYPERGRYPH_TOKEN.txt',
]


def read(path):
    v = []
    with open(path, 'r', encoding='utf-8') as f:
        for i in f.readlines():
            i = i.strip()
            i and i not in v and v.append(i)
    return v


def read_token_file():
    for path in token_files:
        if os.path.exists(path):
            return read(path)
    return []


def handler():
    token = read_token_file()
    if token:
        for i in range(1, len(token)):
            threading.Thread(target=start, args=(token[i],)).start()
        start(token[0])


def start(token):
    try:
        account = nte.parse_account_line(token)
        if not account:
            raise ValueError('账号配置为空')
        nte.do_sign(account)
    except Exception as ex:
        logging.error('签到完全失败了！：', exc_info=ex)


handler()

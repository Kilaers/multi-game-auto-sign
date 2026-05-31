import json
import logging
import os
import time
from datetime import date

import requests

import push
from skyland import start
from kurobbs import start as start_kurobbs
from tajiduo import start as start_tajiduo

exit_when_fail_env = os.environ.get('EXIT_WHEN_FAIL')
use_proxy = os.environ.get('USE_PROXY')

PLATFORM_META = {
    'skyland': {'name': '森空岛（明日方舟 / 终末地）', 'start': start},
    'kurobbs': {'name': '库街区（鸣潮 / 战双帕弥什）', 'start': start_kurobbs},
    'tajiduo': {'name': '塔吉多（幻塔 / 异环）', 'start': start_tajiduo},
}


def config_logger():
    current_date = date.today().strftime('%Y-%m-%d')
    if not os.path.exists('logs'):
        os.mkdir('logs')
    logger = logging.getLogger()

    file_handler = logging.FileHandler(f'./logs/{current_date}.log', encoding='utf-8')
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    def filter_code(text):
        filter_key = ['code', 'cred', 'token']
        try:
            j = json.loads(text)
            if not j.get('data'):
                return text
            data = j['data']
            for i in filter_key:
                if i in data:
                    data[i] = '*****'
            return json.dumps(j, ensure_ascii=False)
        except:
            return text

    _get = requests.get
    _post = requests.post

    def get(*args, **kwargs):
        if use_proxy:
            kwargs.update({
                'proxies': {
                    'https': 'http://localhost:8000',
                },
                'verify': False
            })
        response = _get(*args, **kwargs)
        logger.debug(f'GET {args[0]} - {response.status_code} - {filter_code(response.text)}')
        return response

    def post(*args, **kwargs):
        if use_proxy:
            kwargs.update({
                'proxies': {
                    'https': 'http://localhost:8000',
                },
                'verify': False
            })
        response = _post(*args, **kwargs)
        logger.debug(f'POST {args[0]} - {response.status_code} - {filter_code(response.text)}')
        return response

    requests.get = get
    requests.post = post


def load_platforms() -> dict:
    env_platforms = os.environ.get('PLATFORMS', '').strip()
    if env_platforms:
        enabled = {k: False for k in PLATFORM_META}
        for name in env_platforms.split(','):
            name = name.strip().lower()
            if name in enabled:
                enabled[name] = True
        logging.info(f'从环境变量 PLATFORMS 读取: {[k for k, v in enabled.items() if v]}')
        return enabled

    config_path = 'platforms.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            enabled = {}
            for key in PLATFORM_META:
                enabled[key] = bool(saved.get(key, True))
            return enabled
        except Exception:
            pass

    print()
    print('=' * 50)
    print('  首次运行，请选择需要签到的社区：')
    print('  （输入序号切换，输入 done 完成选择）')
    print('=' * 50)
    print()

    enabled = {key: False for key in PLATFORM_META}
    order = list(PLATFORM_META.keys())

    while True:
        print('当前选择:')
        for i, key in enumerate(order, 1):
            mark = '[√]' if enabled[key] else '[ ]'
            print(f'  {i}. {mark} {PLATFORM_META[key]["name"]}')
        print()
        choice = input('输入序号切换，或输入 done 完成: ').strip().lower()

        if choice == 'done':
            break
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(order):
                key = order[idx]
                enabled[key] = not enabled[key]
                continue
        print('无效输入，请输入序号或 done')

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(enabled, f, ensure_ascii=False, indent=2)

    selected = [k for k, v in enabled.items() if v]
    if not selected:
        print('未选择任何社区，默认全部启用。')
        enabled = {k: True for k in PLATFORM_META}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(enabled, f, ensure_ascii=False, indent=2)

    print()
    print(f'已选择: {", ".join(PLATFORM_META[k]["name"] for k in selected)}')
    print(f'配置已保存到 {config_path}，下次运行将直接使用此配置。')
    print(f'如需修改，删除 {config_path} 即可重新选择。')
    print()
    return enabled


if __name__ == '__main__':
    config_logger()

    logging.info('=========starting==========')

    platforms = load_platforms()

    start_time = time.time()
    all_logs = []
    success = True

    for key, meta in PLATFORM_META.items():
        if not platforms.get(key):
            logging.info(f'{meta["name"]}: 未启用，跳过')
            continue
        try:
            s, logs = meta['start']()
            all_logs.extend(logs)
            if not s:
                success = False
        except Exception as e:
            logging.error(f'{meta["name"]} 签到异常: {e}', exc_info=e)
            all_logs.append(f'{meta["name"]}: 签到异常 - {e}')
            success = False

    push.push(all_logs)
    end_time = time.time()
    logging.info(f'complete with {(end_time - start_time) * 1000} ms')
    logging.info('===========ending============')

    logging.info(f'exit_when_fail_env: {exit_when_fail_env}, success: {success}')
    if (exit_when_fail_env == "on") and not success:
        exit(1)

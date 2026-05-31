# multi-game-auto-sign
多游戏社区以及游戏自动签到（森空岛/库街区/塔吉多）

# multi-game-auto-sign

多游戏社区自动签到脚本，支持 **森空岛**、**库街区**、**塔吉多** 三大平台。

---

## 支持的平台与游戏

| 平台 | 游戏 | 登录方式 |
|------|------|----------|
| **森空岛** (skland.com) | 明日方舟、终末地 | 手机密码 / 验证码 / 手动 Token |
| **库街区** (kurobbs.com) | 鸣潮、战双帕弥什 | 手机验证码 / 抓包 Token |
| **塔吉多** (tajiduo.com) | 幻塔、异环 | 手机密码 / 验证码 / 手动 refreshToken |

首次运行时会弹出菜单，可自由勾选需要签到的平台。

---

## 快速开始

### 环境要求

- Python 3.9+
- `pip install -r requirements.txt`

### 运行

```bash
python src/main.py
```

首次运行会让你选择需要签到的社区，选择后保存为 `platforms.json`，下次直接跳过。

### 添加账号

| 平台 | 命令 |
|------|------|
| 森空岛 | `set SKYLAND_TYPE=add_account && python src/main.py` |
| 库街区 | `set KURO_TYPE=add_account && python src/main.py` |
| 塔吉多 | `set TAJIDUO_TYPE=add_account && python src/main.py` |

---

## Token 获取方式

### 森空岛

运行脚本后选择登录方式即可，会自动保存到 `TOKEN.txt`。

### 库街区
首先试一下能否验证码，不行就采用下面方式（多半过不了人机验证部分）
手机安装库街区 APP → 登录 → 用 Reqable/HttpCanary 抓包 → 复制请求头中的 `token` 字段。脚本支持验证码登录获取。
参考链接 https://fufu.blog/t/164/

### 塔吉多

运行脚本后选择手机密码/验证码登录，会自动保存 `refreshToken` 到 `TAJIDUO_TOKEN.txt`。
---



项目参考
森空岛签到 https://gitee.com/FancyCabbage/skyland-auto-sign
塔吉多签到 https://github.com/Candy-QAQ/NTE-Auto-Sign


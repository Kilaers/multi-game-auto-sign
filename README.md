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

### 森空岛/塔吉多

运行脚本后选择登录方式即可，会自动保存到 `TOKEN.txt`。

### 库街区
首先试一下能否验证码，不行就采用下面方式（多半过不了人机验证部分）··
手机安装库街区 APP → 登录 → 用 Reqable/HttpCanary 抓包 → 复制请求头中的 `token` 字段。脚本支持验证码登录获取。··
参考链接 https://fufu.blog/t/164/


---

## 华为云函数签到
#### 不建议用github action签到！，很大概率被封

1、点击[华为云函数创建](https://console.huaweicloud.com/functiongraph/#/serverless/functions/create?from=dashboard)··

创建账号，密码，实名认证完成后，点击右上角的'创建函数'按钮··

<img width="650" height="423" alt="image" src="https://github.com/user-attachments/assets/e809c38d-9ca5-4b0b-bb8e-6a2f7abe441b" />

2、进入选择运行时环境为定制运行时， 并填一下脚本名称（随便填）。其它设置不用动··

<img width="1172" height="581" alt="image" src="https://github.com/user-attachments/assets/d32f5326-223c-4be7-9562-e1dfd9e04fe4" />

3、将[华为云函数](https://github.com/Kilaers/multi-game-auto-sign/releases/tag/huaweiyun)下载，在函数界面点击右上角的上传zip··

<img width="669" height="309" alt="image" src="https://github.com/user-attachments/assets/2f0517f8-4f5b-4d8b-bcbb-219be9043c7d" />

4、将获取的token填入txt中，注意填入社区的名字，部署代码后再测试

<img width="1356" height="488" alt="image" src="https://github.com/user-attachments/assets/91fbf6e0-868c-4381-981c-b254af021b26" />

5、正常结束后是这个样子的

<img width="974" height="474" alt="image" src="https://github.com/user-attachments/assets/6ec1a6a5-eaef-4671-bc3d-d3ec3960d7b9" />

6、为了让脚本每天执行，我们需要创建一个触发器

<img width="1025" height="637" alt="image" src="https://github.com/user-attachments/assets/f9391002-86a7-4051-bf42-ea37ae417755" />

触发器类型请选择定时触发器

<img width="766" height="835" alt="image" src="https://github.com/user-attachments/assets/bbb75229-f52f-489c-82c7-99c09d3e1df6" />

触发器类型选择Cron表达式
<img width="747" height="674" alt="image" src="https://github.com/user-attachments/assets/c3a2cc42-0362-4cc7-825a-29be071554c3" />

然后填入这串东西0 1 1 * * ? 它指的是每天凌晨1点01分会执行一次
<img width="906" height="831" alt="image" src="https://github.com/user-attachments/assets/d19350a4-7dbb-48cb-a548-f1f802346bd2" />


---
## 其他部署方式
可参考部署方式 https://gitee.com/FancyCabbage/skyland-auto-sign


### 项目参考
森空岛签到 https://gitee.com/FancyCabbage/skyland-auto-sign
塔吉多签到 https://github.com/Candy-QAQ/NTE-Auto-Sign


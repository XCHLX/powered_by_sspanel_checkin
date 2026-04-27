# import json
# import requests, os, time, hmac, hashlib, base64, logging
# from urllib.parse import urlparse, quote_plus
# from datetime import datetime

# from utils import SecureGistManager

# # =============================
# # 配置部分
# # =============================
# CONFIG = os.getenv("CONFIG", "")


# # 账号地址 用户名 密码
# CONFIG = """
# https://ikuuu.org
# chen540605375@gmail.com
# 123456
# https://www.dabai.in
# chen540605375@gmail.com
# chen540605375
# """
# # =============================
# SCKEY = os.getenv("SCKEY")
# DING_WEBHOOK = os.getenv("DINGDINGWEBHOOK")
# DING_SECRET = os.getenv("DINGDINGSECRET")
# G_ID = os.getenv("G_ID")
# G_TOKEN = os.getenv("G_TOKEN")
# TIMEOUT = 15
# RETRY = 2

# platform_urls = {}

# # =============================
# # 日志系统
# # =============================
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
# )


# def log(msg):
#     logging.info(msg)


# # =============================
# # 工具函数
# # =============================
# def is_url(line):
#     return line.startswith("http")


# def is_cookie(line: str) -> bool:
#     """
#     判断字符串是否为 Cookie 格式：
#     典型格式：key=value; key2=value2
#     """
#     if "=" not in line or ";" not in line:
#         return False

#     parts = line.split(";")

#     valid_pairs = 0
#     for part in parts:
#         part = part.strip()
#         if "=" in part:
#             k, v = part.split("=", 1)

#             # 基本合法性校验
#             if k and v:
#                 valid_pairs += 1

#     # 至少有 2 个 key=value 才认为是 cookie（避免误判密码）
#     return valid_pairs >= 2


# def parse_cookie(cookie_str):
#     cookies = {}
#     for item in cookie_str.split(";"):
#         if "=" in item:
#             k, v = item.strip().split("=", 1)
#             cookies[k] = v
#     return cookies


# def get_platform(url):
#     name = urlparse(url).netloc
#     platform_urls[name] = url
#     return name


# # =============================
# # 配置解析（增强版）
# # =============================
# def parse_accounts(text):
#     lines = [l.strip() for l in text.splitlines() if l.strip()]
#     result = {}
#     current = None
#     i = 0

#     while i < len(lines):
#         line = lines[i]

#         # URL
#         if is_url(line):
#             current = line
#             result[current] = []
#             i += 1
#             continue

#         if current:
#             acc = {
#                 "username": None,
#                 "password": None,
#                 "cookie": None,
#             }

#             # 纯 cookie
#             if is_cookie(line):
#                 acc["cookie"] = parse_cookie(line)
#                 result[current].append(acc)
#                 i += 1
#                 continue

#             # 用户名 + 密码 / cookie
#             if i + 1 < len(lines) and not is_url(lines[i + 1]):
#                 acc["username"] = line
#                 acc["password"] = lines[i + 1]

#                 # 👉 如果密码本身是 cookie，直接识别
#                 if is_cookie(acc["password"]):
#                     acc["cookie"] = parse_cookie(acc["password"])

#                 result[current].append(acc)
#                 i += 2
#                 continue

#         i += 1

#     return result


# # =============================
# # 请求封装（带重试）
# # =============================
# def safe_request(session, method, url, **kwargs):
#     for attempt in range(RETRY + 1):
#         try:
#             return session.request(method, url, timeout=TIMEOUT, **kwargs)
#         except Exception as e:
#             log(f"请求失败 {url} 第{attempt+1}次: {e}")
#             time.sleep(2**attempt)
#     raise Exception("请求最终失败")


# # =============================
# # 核心签到逻辑（自动 fallback）
# # =============================
# def checkin(url, acc):
#     session = requests.Session()

#     headers = {
#         "origin": url,
#         "referer": f"{url}/user",
#         "user-agent": "Mozilla/5.0",
#     }

#     login_url = f"{url}/auth/login"
#     check_url = f"{url}/user/checkin"

#     def try_checkin():
#         res = safe_request(session, "POST", check_url, headers=headers)
#         data = res.json()

#         if "未登录" in data.get("msg", ""):
#             raise Exception("未登录")

#         return data.get("msg", "签到成功")

#     print(f"开始处理账号: {acc['username']}")
#     try:
#         fName = f"{get_platform(url)}-{ acc['username']}-config.txt"

#         # 实例化
#         manager = SecureGistManager(G_ID, G_TOKEN, fName)
#         # 2. 读取加密配置并自动解密
#         decrypted_data = manager.get_secure_content(fName)
#         if decrypted_data:
#             cookies_list = json.loads(decrypted_data)
#             # 3. 循环设置到 Session 中
#             for cookie in cookies_list:
#                 if "ip" == cookie["name"]:
#                     continue
#                 session.cookies.set(
#                     name=cookie["name"],
#                     value=cookie["value"],
#                     domain=cookie.get("domain"),
#                     path=cookie.get("path"),
#                 )
#             msg = try_checkin()
#             return True, f"{msg}"
#     except Exception as e:
#         log(f"远端cookies异常,尝试账号密码: {e}")
#     # =====================
#     # 1️⃣ 账号密码登录
#     # =====================
#     if acc.get("username") and acc.get("password"):
#         try:
#             login_data = {
#                 "email": acc["username"],
#                 "passwd": acc["password"],
#             }

#             login_res = safe_request(
#                 session, "POST", login_url, headers=headers, data=login_data
#             )

#             login_json = login_res.json()

#             if login_json.get("ret") == 1:
#                 msg = try_checkin()
#                 return True, f"{msg}"

#             log(f"账号登录失败，  {acc['username']}")

#         except Exception as e:
#             log(f"账号异常，尝试cookie: {e}")

#         # =====================
#         # fallback：password当cookie
#         # =====================
#         try:
#             if is_cookie(acc["password"]):
#                 session.cookies.update(parse_cookie(acc["password"]))
#                 msg = try_checkin()
#                 return True, f"{msg}"
#         except Exception as e:
#             return False, f"账号+cookie失败: {e}"

#     # =====================
#     # 2️⃣ 纯 cookie
#     # =====================
#     if acc.get("cookie"):
#         try:
#             session.cookies.update(acc["cookie"])
#             msg = try_checkin()
#             return True, f"{msg}"
#         except Exception as e:
#             return False, f"cookie失败: {e}"

#     return False, "无有效凭证"


# # =============================
# # 推送
# # =============================
# def send_serverchan(text):
#     if not SCKEY:
#         return
#     url = f"https://sctapi.ftqq.com/{SCKEY}.send"
#     requests.post(url, data={"title": "签到结果", "desp": text})


# def send_dingtalk(text):
#     if not DING_WEBHOOK or not DING_SECRET:
#         return

#     timestamp = str(round(time.time() * 1000))
#     sign_str = f"{timestamp}\n{DING_SECRET}".encode()

#     sign = quote_plus(
#         base64.b64encode(
#             hmac.new(DING_SECRET.encode(), sign_str, hashlib.sha256).digest()
#         )
#     )

#     webhook = f"{DING_WEBHOOK}&timestamp={timestamp}&sign={sign}"

#     data = {"msgtype": "markdown", "markdown": {"title": "签到结果", "text": text}}

#     requests.post(webhook, json=data)


# # =============================
# # Markdown 报告
# # =============================
# def build_md(data):
#     success_count = 0
#     fail_count = 0
#     md = ["## 📌 每日自动签到结果通知\n"]

#     for platform, accounts in data.items():
#         md.append(f"### 🌐 平台：{platform}")
#         md.append(f"**地址**：{platform_urls.get(platform, '未知地址')}\n")

#         for acc in accounts:
#             username = acc["username"]

#             if acc["success"]:
#                 success_count += 1
#                 md.append(f"- ✅ **{username}**")
#                 md.append(f"  - 状态：签到成功 🎉")
#                 md.append(f"  - 说明：{acc['msg']}\n")
#             else:
#                 fail_count += 1
#                 md.append(f"- ❌ **{username}**")
#                 md.append(f"  - 状态：签到失败 ⚠️")
#                 md.append(f"  - 原因：{acc['msg']}\n")

#         md.append("---\n")

#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     md.append("### 📊 统计汇总")
#     md.append(f"- 成功：**{success_count}** 个账号")
#     md.append(f"- 失败：**{fail_count}** 个账号")
#     md.append(f"- 执行时间：`{now}`\n")
#     md.append("> 🤖 自动任务执行完毕")

#     return "\n".join(md)


# # =============================
# # 主流程
# # =============================
# def main():
#     accounts = parse_accounts(CONFIG)
#     # # 输出 JSON
#     accountObject = json.dumps(accounts, ensure_ascii=False, indent=4)
#     # print(accountObject)
#     print("开始签到...")
#     result = {}
#     for url, accs in accounts.items():
#         platform = get_platform(url)
#         result[platform] = []

#         for acc in accs:
#             try:
#                 log(f"开始签到: {platform}")

#                 ok, msg = checkin(url, acc)

#                 username = acc.get("username")

#                 result[platform].append(
#                     {
#                         "username": username,
#                         "success": ok,
#                         "msg": msg,
#                     }
#                 )

#                 log(f"结果: {msg}")

#             except Exception as e:
#                 result[platform].append(
#                     {
#                         "username": acc.get("username", "未知"),
#                         "success": False,
#                         "msg": str(e),
#                     }
#                 )

#     md = build_md(result)
#     print(md)

#     send_serverchan(md)
#     send_dingtalk(md)


# if __name__ == "__main__":
#     main()


import json
from datetime import datetime

from config import CONFIG
from logger import init_logger, log
from parser import parse_accounts
from utils import get_platform, platform_urls
from checkin import checkin
from notify import send_serverchan, send_dingtalk


# =============================
# Markdown 报告
# =============================
def build_md(data):
    success_count = 0
    fail_count = 0
    md = ["## 📌 每日自动签到结果通知\n"]

    for platform, accounts in data.items():
        md.append(f"### 🌐 平台：{platform}")
        md.append(f"**地址**：{platform_urls.get(platform, '未知地址')}\n")

        for acc in accounts:
            username = acc["username"]

            if acc["success"]:
                success_count += 1
                md.append(f"- ✅ **{username}**")
                md.append(f"  - 状态：签到成功 🎉")
                md.append(f"  - 说明：{acc['msg']}\n")
            else:
                fail_count += 1
                md.append(f"- ❌ **{username}**")
                md.append(f"  - 状态：签到失败 ⚠️")
                md.append(f"  - 原因：{acc['msg']}\n")

        md.append("---\n")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md.append("### 📊 统计汇总")
    md.append(f"- 成功：**{success_count}** 个账号")
    md.append(f"- 失败：**{fail_count}** 个账号")
    md.append(f"- 执行时间：`{now}`\n")
    md.append("> 🤖 自动任务执行完毕")

    return "\n".join(md)


def main():
    init_logger()

    accounts = parse_accounts(CONFIG)

    result = {}

    for url, accs in accounts.items():
        platform = get_platform(url)
        result[platform] = []

        for acc in accs:
            log(f"开始: {platform}-{acc.get('username')}")
            ok, msg = checkin(url, acc)

            result[platform].append(
                {"username": acc.get("username"), "success": ok, "msg": msg}
            )

    md = build_md(result)

    print(md)
    send_serverchan(md)
    send_dingtalk(md)


if __name__ == "__main__":
    main()

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

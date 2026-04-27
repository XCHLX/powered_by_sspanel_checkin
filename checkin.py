import json
import requests
from utils import is_cookie, parse_cookie, get_platform
from http_client import safe_request
from logger import log
from config import G_ID, G_TOKEN
from gist import SecureGistManager


def checkin(url, acc):
    session = requests.Session()

    headers = {
        "origin": url,
        "referer": f"{url}/user",
        "user-agent": "Mozilla/5.0",
    }

    login_url = f"{url}/auth/login"
    check_url = f"{url}/user/checkin"

    def try_checkin():
        res = safe_request(session, "POST", check_url, headers=headers)
        data = res.json()

        if "未登录" in data.get("msg", ""):
            raise Exception("未登录")

        return data.get("msg", "签到成功")

    try:
        fname = f"{get_platform(url)}-{acc['username']}-config.txt"
        manager = SecureGistManager(G_ID, G_TOKEN, fname)

        decrypted = manager.get_secure_content(fname)
        if decrypted:
            cookies = json.loads(decrypted)
            for c in cookies:
                if c["name"] == "ip":
                    continue
                session.cookies.set(
                    c["name"], c["value"], domain=c.get("domain"), path=c.get("path")
                )
            return True, try_checkin()

    except Exception as e:
        log(f"远端cookie失败: {e}")

    # 账号密码
    if acc.get("username") and acc.get("password"):
        try:
            res = safe_request(
                session,
                "POST",
                login_url,
                headers=headers,
                data={"email": acc["username"], "passwd": acc["password"]},
            )

            if res.json().get("ret") == 1:
                return True, try_checkin()

        except Exception as e:
            log(f"账号登录异常: {e}")

        # fallback cookie
        if is_cookie(acc["password"]):
            session.cookies.update(parse_cookie(acc["password"]))
            return True, try_checkin()

    # 纯 cookie
    if acc.get("cookie"):
        session.cookies.update(acc["cookie"])
        return True, try_checkin()

    return False, "无有效凭证"

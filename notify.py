import time, hmac, hashlib, base64, requests
from urllib.parse import quote_plus
from config import SCKEY, DING_WEBHOOK, DING_SECRET


def send_serverchan(title, text):
    if not SCKEY:
        return

    url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    requests.post(url, data={"title": {title}, "desp": text})


def send_dingtalk(text):
    if not DING_WEBHOOK or not DING_SECRET:
        return

    timestamp = str(round(time.time() * 1000))
    sign_str = f"{timestamp}\n{DING_SECRET}".encode()

    sign = quote_plus(
        base64.b64encode(
            hmac.new(DING_SECRET.encode(), sign_str, hashlib.sha256).digest()
        )
    )

    webhook = f"{DING_WEBHOOK}&timestamp={timestamp}&sign={sign}"

    data = {"msgtype": "markdown", "markdown": {"title": "签到结果", "text": text}}

    requests.post(webhook, json=data)

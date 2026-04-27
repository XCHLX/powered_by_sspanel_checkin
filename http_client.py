import time
import requests
from config import TIMEOUT, RETRY
from logger import log


def safe_request(session, method, url, **kwargs):
    for attempt in range(RETRY + 1):
        try:
            return session.request(method, url, timeout=TIMEOUT, **kwargs)
        except Exception as e:
            log(f"请求失败 {url} 第{attempt+1}次: {e}")
            time.sleep(2**attempt)

    raise Exception("请求最终失败")

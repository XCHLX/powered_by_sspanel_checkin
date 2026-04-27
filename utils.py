import os
import json
import base64
import requests
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from urllib.parse import urlparse

platform_urls = {}


def is_url(line):
    return line.startswith("http")


def is_cookie(line: str) -> bool:
    if "=" not in line or ";" not in line:
        return False

    parts = line.split(";")
    valid_pairs = 0

    for part in parts:
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            if k and v:
                valid_pairs += 1

    return valid_pairs >= 2


def parse_cookie(cookie_str):
    cookies = {}
    for item in cookie_str.split(";"):
        if "=" in item:
            k, v = item.strip().split("=", 1)
            cookies[k] = v
    return cookies


def get_platform(url):
    name = urlparse(url).netloc
    platform_urls[name] = url
    return name


# --- 使用场景演示 ---
if __name__ == "__main__":
    pass

import os


def get_config(name: str, local_file: str = None, required: bool = True):
    """
    name: 环境变量名
    local_file: 本地文件路径（可选）
    required: 是否必须
    """

    # 1️⃣ 优先环境变量（正式环境）
    value = os.getenv(name)
    if value:
        print(f"[ENV] {name} loaded from environment")
        return value

    # 2️⃣ 本地文件兜底
    if name:
        if os.path.exists(f"debug/{name}.txt"):
            with open(f"debug/{name}.txt", "r", encoding="utf-8") as f:
                value = f.read().strip()
                if value:
                    print(f"[LOCAL] {name} loaded from {local_file}")
                    return value

    return None


CONFIG = get_config("CONFIG")
SCKEY = get_config("SCKEY")
DING_WEBHOOK = get_config("DINGDINGWEBHOOK")
DING_SECRET = get_config("DINGDINGSECRET")

G_ID = get_config("G_ID")
G_TOKEN = get_config("G_TOKEN")


TIMEOUT = 15
RETRY = 2

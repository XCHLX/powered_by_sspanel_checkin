import json
import time
import os
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
from webdriver_manager.chrome import ChromeDriverManager

from config import CONFIG, G_ID, G_TOKEN
from gist import SecureGistManager
from logger import init_logger, log
from parser import parse_accounts
from utils import get_platform


def get_chrome_main_version():
    # 获取驱动管理器检测到的安装版本（例如 "123.0.6312.122"）
    full_version = ChromeDriverManager().driver.get_browser_version_from_os()
    # 提取主版本号 (例如 "123")
    main_version = int(full_version.split(".")[0])
    return main_version


def save_cookies(email, password, gistmanager: SecureGistManager):
    options = uc.ChromeOptions()
    # 模拟真实浏览器特征
    options.add_argument("--window-size=1920,1080")
    os.makedirs("screenshotstemp", exist_ok=True)

    # 使用 context manager (with 语句) 可以自动处理资源回收，减少句柄报错
    try:
        # driver = uc.Chrome(options=options, version_main=147)
        options.add_argument("--headless")  # 必须：无界面模式
        options.add_argument("--no-sandbox")  # 必须：解决权限问题
        options.add_argument("--disable-dev-shm-usage")  # 必须：防止内存不足
        options.add_argument("--remote-debugging-port=9222")  # 建议：有助于连接稳定
        # driver = uc.Chrome(options=options)
        version = get_chrome_main_version()
        print(f"🚀 检测到 Chrome 主版本: {version}")
        driver = uc.Chrome(options=options, version_main=version)
        driver.get("https://ikuuu.org/user")
        time.sleep(2)
        wait = WebDriverWait(driver, 15)
        # ====================== 1. 点击极验验证按钮 ======================
        try:
            driver.save_screenshot("screenshotstemp/01_after_click_geetest1.png")
            geetest_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[class*='geetest_btn_click']")
                )
            )
            print("找到极验按钮，正在点击...")
            geetest_btn.click()
            time.sleep(2.5)  # 等待验证码加载

            driver.save_screenshot("screenshotstemp/01_after_click_geetest.png")

        except Exception as e:
            print("点击极验按钮失败:", e)
            driver.save_screenshot("screenshotstemp/geetest_click_fail.png")

        # ====================== 2. 填写邮箱 ======================
        try:
            driver.save_screenshot("screenshotstemp/02_after_fill_email2.png")

            email_input = wait.until(EC.element_to_be_clickable((By.ID, "email")))
            email_input.clear()
            email_input.send_keys(email)  # ← 修改成你的邮箱
            print("✅ 邮箱填写完成")
            driver.save_screenshot("screenshotstemp/02_after_fill_email.png")
        except Exception as e:
            print("填写邮箱失败:", e)
            driver.save_screenshot("screenshotstemp/email_fail.png")

        # ====================== 3. 填写密码 ======================
        try:
            driver.save_screenshot("screenshotstemp/03_after_fill_password3.png")

            password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))
            password_input.clear()
            password_input.send_keys(password)  # ← 修改成你的密码
            print("✅ 密码填写完成")
            driver.save_screenshot("screenshotstemp/03_after_fill_password.png")
        except Exception as e:
            print("填写密码失败:", e)
            driver.save_screenshot("screenshotstemp/password_fail.png")

        try:
            # 定位包含 .login 类的 submit 按钮
            login_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.login"))
            )
            print("找到登录按钮，正在点击...")
            login_btn.click()
            print("✅ 登录按钮已点击")
            driver.save_screenshot("screenshotstemp/04_after_fill_login.png")

        except Exception as e:
            print("点击登录按钮失败:", e)

        # 优化：循环检测是否登录成功，不需要死等 60 秒
        for i in range(60):
            if "user" in driver.current_url:
                print("\n检测到已进入后台，登录成功！")
                break
            if i % 5 == 0:
                print(f"等待中... 剩余 {60-i}s", end="\r")
            time.sleep(1)
        driver.save_screenshot("screenshotstemp/04_login.png")

        # 获取当前域名的 cookies
        cookies = driver.get_cookies()
        with open("screenshotstemp/ikuuu_cookies.json", "w") as f:
            json.dump(cookies, f)

        gistmanager.update_secure_content(fname, json.dumps(cookies))

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        # 显式退出，并捕获 Windows 句柄异常
        try:
            driver.quit()
        except:
            pass


def login_with_cookies(fname):
    gistmanager = SecureGistManager(G_ID, G_TOKEN, fname)
    cookies = gistmanager.get_secure_content(fname)
    print(json.loads(cookies))


if __name__ == "__main__":

    init_logger()
    # 必须在 Windows 下使用此判断，防止多进程递归启动
    accounts = parse_accounts(CONFIG)
    log(f"共找到 {len(accounts)} 个账号")
    for url, accs in accounts.items():
        if "ikuuu" in url:
            for acc in accs:
                fname = f"{get_platform(url)}-{acc['username']}-config.txt"
                log(f"开始: {fname}====={acc.get("username")}")
                gistmanager = SecureGistManager(G_ID, G_TOKEN, fname)
                save_cookies(acc.get("username"), acc.get("password"), gistmanager)

    # while True:
    #     time.sleep(100)

import os
import json
import time
import logging

from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
from settings import DOUYIN_COOKIE_PATH, DOUYIN_CSV_PATH, SCROLL_TIME, WEBDRIVER_PATH, LOG_PATH


def get_logger():
    global logger
    if logger is not None:
        return logger
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    log_file = "douyin_crawls.log"
    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('douyin_crawls_logger')
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(sh)
    logger.info('logger init finished ---- log file: {}'.format(log_file))
    return logger


class DouyinSpider:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +
                                    ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
        proxy_server = Server(r'')

        s = Service(WEBDRIVER_PATH)
        self.browser = webdriver.Chrome(service=s, options=chrome_options)
        self.logger = get_logger()
        self._update_cookie()

    def _update_cookie(self):
        self.browser.get('https://www.douyin.com')
        time.sleep(5)
        if not os.path.exists(DOUYIN_COOKIE_PATH):
            time.sleep(40)  # 留够时间来手动登录
            with open(DOUYIN_COOKIE_PATH, 'w') as f:
                # 将cookies保存为json格式在cookies.txt中
                f.write(json.dumps(self.browser.get_cookies()))
        else:
            self.browser.delete_all_cookies()
            with open(DOUYIN_COOKIE_PATH, 'r') as f:
                cookies_list = json.load(f)  # 读取cookies
                for cookie in cookies_list:
                    if isinstance(cookie.get('expiry'), float):
                        cookie['expiry'] = int(cookie['expiry'])
                    try:
                        self.browser.add_cookie(cookie)  # 加入cookies
                    except:
                        self.logger.info("add cookie fail!!!!")
                        self.logger.info(cookie)
            self.browser.refresh()

    def search(self,
               keyword: str,
               publish_time=0,
               sort_type=0,
               scroll_time = 50):
        url = "https://www.douyin.com/search/{}?publish_time={}&sort_type={}".format(keyword, publish_time, sort_type)
        self.browser.get(url)
        self.browser.maximize_window()
        time.sleep(5)
        # 宫格预览
        self.browser.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div[2]").click()

    def _scroll_to_bottom(self, scroll_time: int):
        for i in range(scroll_time):
            pyautogui.scroll(-400)
            time.sleep(0.2)

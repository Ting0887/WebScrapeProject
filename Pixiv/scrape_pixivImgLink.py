from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import time
import datetime
import os
from bs4 import BeautifulSoup
import requests

    
def login_account(email, pwd):
    browser.get('https://accounts.pixiv.net/login')
    browser.find_element(By.XPATH, '//fieldset[@class="sc-bn9ph6-0 bYwpCj sc-2o1uwj-4 jZgbmK"]/label[@class="sc-bn9ph6-1 hMUThl"]/input').send_keys(email)
    browser.find_element(By.XPATH, '//fieldset[@class="sc-bn9ph6-0 bYwpCj sc-2o1uwj-5 duclA-d"]/label[@class="sc-bn9ph6-1 hMUThl"]/input').send_keys(pwd)
    time.sleep(0.3)
    b = browser.find_element(By.XPATH, '//button[@class="sc-aXZVg fSnEpf sc-eqUAAy hhGKQA sc-2o1uwj-10 ldVSLT sc-2o1uwj-10 ldVSLT"]')
    browser.execute_script("arguments[0].click();", b)
        
def parse_ImgLink(page):
    while page <= 500:
        bookmarkURL = f"https://www.pixiv.net/users/15904794/bookmarks/artworks?p={page}"
        browser.get(bookmarkURL)
        time.sleep(1)
        
        # get all Pixiv img link
        soup = BeautifulSoup(browser.page_source,"lxml")
        allimg = soup.find_all("div", class_="sc-cdtm3u-0 cKkVHN")
        for img in allimg:
            imglink = "https://www.pixiv.net"+img.find("a")["href"]
            with open("test.txt","a",encoding="utf-8") as txt:
                txt.write(imglink+"\n")
            txt.close()
        page += 1

if __name__ == '__main__':
    chrome_options = Options()
    prefs = {"profile.default_content_setting_values.notifications": 2}

    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_argument("--disable-3d-apis")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--in-process-plugins")
    
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service,options=chrome_options)
    with open("account.txt", "r", encoding="utf-8") as txt:
        data = txt.read().splitlines()
        print(data)
        email = data[0]
        pwd = data[1]
    login_account(email, pwd)
    time.sleep(2)
    
    page = int(input("請輸入抓取總頁數:"))
    parse_ImgLink()
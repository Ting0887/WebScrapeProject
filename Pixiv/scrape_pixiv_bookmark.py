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

    
def login_account(email,pwd):
    browser.get('https://accounts.pixiv.net/login')
    browser.find_element(By.XPATH, '//fieldset[@class="sc-bn9ph6-0 bYwpCj sc-2o1uwj-4 jZgbmK"]/label[@class="sc-bn9ph6-1 hMUThl"]/input').send_keys(email)
    browser.find_element(By.XPATH, '//fieldset[@class="sc-bn9ph6-0 bYwpCj sc-2o1uwj-5 duclA-d"]/label[@class="sc-bn9ph6-1 hMUThl"]/input').send_keys(pwd)
    time.sleep(0.3)
    b = browser.find_element(By.XPATH, '//button[@class="sc-aXZVg fSnEpf sc-eqUAAy hhGKQA sc-2o1uwj-10 ldVSLT sc-2o1uwj-10 ldVSLT"]')
    browser.execute_script("arguments[0].click();", b)
    time.sleep(60)

def parse_Img(imglink):
    collect_img = []
    browser.get(imglink)
    time.sleep(1)
    # click 查看內容，如果圖片超過某個數量時，需要點擊按鈕
    try:
        clickmore = browser.find_element(By.XPATH, '//div[@class="sc-emr523-2 drFRmD"]')
        browser.execute_script("arguments[0].click();", clickmore)
        time.sleep(1)
    except:
        pass
    
    # parse Image on this URL
    soup = BeautifulSoup(browser.page_source,"lxml")
    
    # two cases
    try:
        firstimg = soup.find("div",class_="sc-1e1hy3c-2 dSqYyx gtm-medium-work-expanded-view").find("a")["href"]
        lastimg = soup.find("div",class_="sc-1e1hy3c-2 dSqYyx gtm-illust-work-scroll-finish-reading").find("a")["href"]
        save_pic(firstimg)
        save_pic(lastimg)
        
        divs = soup.find_all("div",class_="sc-1e1hy3c-2 dSqYyx")
        for div in divs:
            img = div.find("div",class_="sc-1qpw8k9-0 eXiEBZ").find("a")["href"]
            print(img)
            save_pic(img)
    except:
        pass
    
    try:
        divs = soup.find_all("div",class_="sc-1oz5uvo-4 iKsoAt")
        for div in divs:
            img = div.find("a")["href"]
        print(img)
        save_pic(img)
    except:
        pass

    try:
        img = soup.find("div",class_="sc-1qpw8k9-0 gTFqQV").find("a")["href"]
        print(img)
        save_pic(img)
    except:
        pass
    
    return collect_img

def read_Imglink():
    with open("PixivImg_link.txt", "r", encoding="utf-8") as txt:
        for imglink in txt.read().splitlines():
            parse_Img(imglink)

def save_pic(img):
    # if dest_Dir not exist,building dir
    dest_Dir = 'my_favorite'
    if os.path.exists(dest_Dir) == False:
        os.mkdir(dest_Dir)
    
    headers = {'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    try:
        picture = requests.get(img, headers = headers, timeout=10)
        picture.raise_for_status()
        print('%s 圖片下載成功!!!'%img)
        
        # open file and save these pics
        picFile = open(os.path.join(dest_Dir, os.path.basename(img)),'wb')
        for diskStorage in picture.iter_content(10240):
            picFile.write(diskStorage)
        picFile.close()
    except:
        print("下載失敗")
        

if __name__ == '__main__':
    chrome_options = Options()
    prefs = {"profile.default_content_setting_values.notifications": 2}

    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_argument("--disable-3d-apis")
    chrome_options.add_argument('--no-sandbox')
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
    read_Imglink()
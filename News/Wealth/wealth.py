import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def setup_browser():
    """设置并返回一个 Selenium WebDriver 实例。"""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
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
    return webdriver.Chrome(service=service, options=chrome_options)

def teardown_browser(browser):
    browser.quit()

def scroll_and_collect_data(browser):
    js_down = 'window.scrollTo(0, document.body.scrollHeight)'
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        browser.execute_script(js_down)
        time.sleep(2.5)

        soup = BeautifulSoup(browser.page_source, 'lxml')
        items = soup.find_all('div', 'dpH7T')

        for item in items:
            date_time = extract_date(item)
            print(date_time)

        try:
            button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="想看更多"]')))
            button.click()
        except Exception as e:
            print(f"An error occurred while clicking 'More': {e}")
            break

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_content(soup):
    content = []
    try:
        contents = soup.find_all('p', 'qdr-paragraph')
        for c in contents:
            text = c.get_text()
            cleaned_text = text.replace('\ufeff', '').strip()
            content.append(cleaned_text)
    except AttributeError as e:
        print(f"An error occurred: {e}")
    return '\n'.join(content)

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('a', 'Vvwcb a0OGQ Dhqmu T_RGN lz9m3')
        keyword = '、'.join(k.text for k in keywords)
    except Exception as e:
        print(f"An error occurred while extracting keywords: {e}")
    return keyword

def write_to_json(article, folder):
    folder_path = f'news_data/wealth/{folder}/{time.strftime("%Y-%m")}'
    os.makedirs(folder_path, exist_ok=True)
    filename = f'wealth_{folder}{time.strftime("%Y%m%d")}.json'
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'w', encoding='utf8') as jf:
        json.dump(article, jf, ensure_ascii=False, indent=2)

def extract_title(item):
    try:
        return item.find('h2').text
    except AttributeError:
        return ''

def extract_date(item):
    try:
        return item.find('span', 'g4jRc aDT8p pfH6t t1DSN rUO_L').text
    except AttributeError:
        return ''

def extract_author(item):
    try:
        return item.find_all('span', 'g4jRc aDT8p pfH6t t1DSN rUO_L Pm9CI c_Ei3')[1].text
    except IndexError:
        return ''

def extract_link(item):
    try:
        return 'https://www.wealth.com.tw' + item.select('a')[2]['href']
    except IndexError:
        return ''

def Wealth(label, label_id, folder, browser, end_date):
    url = f'https://www.wealth.com.tw/lists/categories/{label_id}'
    browser.get(url)

    time.sleep(2) 
    try:
        browser.find_element(By.XPATH, '//button[text()="我知道了"]').click()
    except Exception as e:
        print(f"An error occurred while clicking 'I Know': {e}")

    scroll_and_collect_data(browser)

    article = []
    soup = BeautifulSoup(browser.page_source, 'lxml')
    items = soup.find_all('div', 'dpH7T')

    for item in items:
        title = extract_title(item)
        date_time = extract_date(item)
        author = extract_author(item)
        link = extract_link(item)

        if date_time < end_date:
            break

        browser.get(link)
        time.sleep(1)  
        soup = BeautifulSoup(browser.page_source, 'lxml')
        content = extract_content(soup)
        keyword = extract_keyword(soup)

        post = {
            "title": title,
            "author": author,
            "date_time": date_time,
            "link": link,
            "label": label,
            "website": "財訊",
            "content": content,
            "keyword": keyword.rstrip('、')
        }
        print(post)
        article.append(post)
        time.sleep(1.5)  

    if article:
        write_to_json(article, folder)

if __name__ == '__main__':
    browser = setup_browser()

    start_date = datetime.datetime.today()
    end_date = (start_date - datetime.timedelta(days=7)).strftime('%Y/%m/%d')

    categories = [
        ('國際', '2c6379e9-7527-442b-880a-bb9552689e06', 'global'),
        ('政經', '352be1d4-7ce8-42b8-9a84-0f491f7927ea', 'politics'),
        ('科技', '79c03f3f-d546-4551-a05f-c6d38e5579ca', 'tech'),
        ('財經', 'd1354fa3-82bf-42e6-84ad-9e36d7615892', 'finance'),
        ('生技醫療', 'dd2b5859-96aa-42bb-b5cc-08e6c7c8728e', 'biotech_medical')
    ]

    for label, label_id, folder in categories:
        Wealth(label, label_id, folder, browser, end_date)

    teardown_browser(browser)

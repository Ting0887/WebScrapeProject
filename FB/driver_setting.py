from selenium import webdriver 

def driver_setting():
    #chromedriver setting
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    # if you don't want to open browser, add 18th line 
    #chrome_options.add_argument("--headless")
    
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option('prefs', prefs)
    prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096, 'intl.accept_languages': 'en-US'}
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('blink-settings=imagesEnabled=false') 
    chrome_options.add_argument("--disable-javascript") 
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--in-process-plugins")
    chrome_options.add_argument('--no-sandbox')
    
    
    ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
    chrome_options.add_argument("user-agent={}".format(ua))
 
  
    return chrome_options
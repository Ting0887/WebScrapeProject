import re
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from driver_setting import driver_setting
from handle_elements import handle_likes,handle_share,handle_comment,handle_posttime
import time
import pandas as pd

class FB_crawler:
    def __init__(self,driverPath,FB_URL,account,password,file_name,end_date):
        self.driverPath = driverPath
        self.FB_URL = FB_URL
        self.account = account
        self.password = password
        self.file_name = file_name
        self.end_date = end_date
        
    def login_fb(self):
        browser = webdriver.Chrome(self.driverPath,chrome_options=driver_setting())
        #FB login
        login_url = 'https://www.facebook.com/'
        browser.get(login_url)
        browser.find_element(By.ID, "email").send_keys(self.account) #input account
        browser.find_element(By.ID, "pass").click()
        browser.find_element(By.ID, "pass").send_keys(self.password) #input password
        browser.find_element(By.NAME, "login").click()
        return browser
    
    def scroll_down(self):
        browser = self.login_fb()
        time.sleep(1.5)
        
        browser.get(self.FB_URL)
        time.sleep(1.5)
        
        js = 'window.scrollTo(0, document.body.scrollHeight)'
        browser.execute_script(js)
        soup = BeautifulSoup(browser.page_source,'lxml')               
        postlist = soup.select('._55wo')
              
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:
             try:
                 browser.set_script_timeout(10)
                 browser.execute_script(js)
                 soup = BeautifulSoup(browser.page_source,'lxml')   
                 postlist = soup.select('._55wo')
                 for post in postlist:
                     try:
                         post_time = post.find('abbr').text                     
                     except:
                         pass
                 time.sleep(3)
    
                 post_time = handle_posttime(post_time)
                 print(post_time)
                    
                 if post_time < self.end_date:
                     break             
                 #if scroll down to bottom
                 new_height = browser.execute_script("return document.body.scrollHeight")
                 if new_height == last_height:
                     break
                 last_height = new_height
             except Exception as e:
                 print(e)
                 pass
        
        self.extract_postdata(postlist)
    
    def extract_postdata(self,postlist):
        save_data = []
        for post in postlist:
            post_source = self.scrape_source(post)
            post_date = self.scrape_date(post)
            post_like = self.scrape_like(post)
            post_share = self.scrape_share(post)
            post_comment = self.scrape_comment(post)
            post_link = self.scrape_postlink(post)
            post_content = self.scrape_content(post)
            
            df = pd.DataFrame([{'source':post_source,
                                'date':post_date,
                                'like':post_like,
                                'share':post_share,
                                'comment':post_comment,
                                'link':post_link,
                                'content':post_content,
                                }])
            
            save_data.append(df)
        self.write_to_csv(save_data)
        
    def write_to_csv(self,save_data):
        merge = pd.concat(save_data,ignore_index=True)
        merge.to_csv(self.file_name+'.csv',index=0,encoding='utf-8-sig')
    
    def scrape_source(self,post):
        try:
             source = post.find('h3',{'data-gt':'{"tn":"C"}'}).strong.text
        except:
             source = ''
            
        return source
    
    def scrape_date(self,post):
        try:                   
            date_time = post.find('abbr').text
        except:
            date_time = ''            
        date_time = handle_posttime(date_time)
        
        return date_time
    
    def scrape_like(self,post):
        try:
            likes = post.find('div','_1g06').text.replace(',','')
        except:
            likes = '0'
        likes = handle_likes(likes)
        
        return likes
    
    def scrape_comment(self,post):
        try:
            comments_count = post.find('span',{'data-sigil':'comments-token'}).text.replace(',','').replace('則留言','')
        except:
            comments_count = '0'
        comments_count = handle_comment(comments_count)
        
        return comments_count
    
    def scrape_share(self,post):
        try:
            shares_count = post.find_all('span','_1j-c',string = re.compile('次分享$'))[0].text.replace(',','').replace('次分享','')
        except:
            shares_count = '0'
        shares_count = handle_share(shares_count)
        
        return shares_count
    
    def scrape_postlink(self,post):
        try:
            post_link = 'https://m.facebook.com' + post.find('a','_5msj')['href'].replace('&substory_index=0','')
            post_link = post_link.split('&')[0] + '&' + post_link.split('&')[1] 
        except:
            post_link = ''
        
        return post_link
    
    def scrape_content(self,post):
        try:
            article_content = post.find('div','_5rgt _5nk5 _5msi').text
        except:
            article_content = ''
        return article_content


    

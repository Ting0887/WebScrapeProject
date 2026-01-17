import pandas as pd 
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By
from handle_date import convert_time
from set_driver import driver_setting


class FB_Crawler:
    def __init__(self,driverPath,account,password,FB_URL,comment_limit,output_file):
        self.driverPath = driverPath
        self.account = account
        self.password = password
        self.FB_URL = FB_URL
        self.comment_limit = comment_limit
        self.output_file = output_file
    
    def set_driver(self):
        browser = webdriver.Chrome(self.driverPath,chrome_options=driver_setting())
        return browser
    
    def login_fb(self):
        browser = self.set_driver()
        #FB login
        login_url = 'https://www.facebook.com/'
        browser.get(login_url)
        browser.find_element(By.ID, "email").send_keys(self.account) 
        browser.find_element(By.ID, "pass").click()
        browser.find_element(By.ID, "pass").send_keys(self.password) 
        browser.find_element(By.NAME, "login").click()
        
        return browser
    def scroll_down(self):
        browser = self.login_fb()
        time.sleep(1.5)
        browser.get(self.FB_URL)
        soup = BeautifulSoup(browser.page_source,'lxml')
        
        last_height = browser.execute_script("return document.body.scrollHeight")
        js = 'window.scrollTo(0, document.body.scrollHeight)'
        comment_c = soup.find_all('div','_2b04')   
        while True:
            browser.execute_script(js)   
            time.sleep(1.5)
            #click more button
            try:
                browser.find_element(By.LINK_TEXT, "查看更多留言…").click()
            except:
                break
 
            soup = BeautifulSoup(browser.page_source,'lxml')
            comment_c = soup.find_all('div','_2b04')
            print(len(comment_c))            
            
            #if comment > 100 break
            if len(comment_c) >= self.comment_limit:
                break
            time.sleep(1)
            
            #if scroll down to bottom
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        #scrape reply
        while True:
            #click reply more
            time.sleep(1.5)
            try:
                ele_reply = browser.find_element_by_xpath("//span[@class='_4ayk']")
                ele_reply.click()
            except:
                break
            
            soup = BeautifulSoup(browser.page_source,'lxml')
            
            #reply more button
            try:
                browser.find_element_by_xpath("//a[@class='async_elem']").click()
            except:
                continue       
        self.get_comment(soup)
        
    def get_comment(self,soup):
        comment_data = []
        comment_bar = soup.find_all('div',{'data-sigil':'comment'})
        for c in comment_bar:
            comment_username = FB_comment().comment_username(c)
            comment_userlink = FB_comment().comment_userlink(c)
            comment_text = FB_comment().comment_text(c)
            comment_time = FB_comment().comment_time(c)
            
            df = pd.DataFrame([{'comment_username':comment_username,
                                'comment_userlink':comment_userlink,
                                'comment_text':comment_text,
                                'comment_time':comment_time}])
            comment_data.append(df)

        reply_bar = soup.find_all('div',{'data-sigil':'comment inline-reply'})
        for r in reply_bar:
            print(r)
            reply_username = FB_reply().reply_username(r)
            reply_userlink = FB_reply().reply_userlink(r)
            reply_text =  FB_reply().reply_text(r)
            reply_time = FB_reply().reply_time(r)
            
            df = pd.DataFrame([{'comment_username':reply_username,
                                'comment_userlink':reply_userlink,
                                'comment_text':reply_text,
                                'comment_time':reply_time}])
            comment_data.append(df)
        self.write_to_csv(comment_data)

    def write_to_csv(self,comment_data):
        df = pd.concat(comment_data,ignore_index=True)
        df.to_csv(self.output_file + '.csv',index=0,encoding='utf-8-sig')
    
class FB_comment:        
    def comment_username(self,c):
        #comment name
        try:
            comment_name = c.find('div','_2b05').a.text.replace('頭號粉絲','')
        except:
            comment_name = ''
        
        return comment_name
        
    def comment_userlink(self,c):
        try:
            p = 'https://www.facebook.com' + c.find('div','_2b05').a.get('href')
            profile_link = p.split('&')[0].replace('?fref=nf','')
        except:
            profile_link = ''
            
        return profile_link
    
    def comment_text(self,c):
        try:
            comment_text = c.find('div',{'data-sigil':'comment-body'}).text.replace('\n','').replace('\t','')
        except:
            comment_text = ''
            
        return comment_text
    
    def comment_time(self,c):
        try:
            comment_time = c.find('abbr').text
            comment_time = convert_time(comment_time)
        except:
            comment_time = ''
        return comment_time     
   
    
class FB_reply:
    def reply_username(self,r):
         try:
             reply_name = r.find('div','_2b05').a.text.replace('頭號粉絲','')
         except:
             reply_name = ''   
         return reply_name
     
    def reply_userlink(self,r):
        try:
            p = 'https://www.facebook.com' + r.find('div','_2b05').a.get('href')
            profile_link = p.split('&')[0].replace('?fref=nf','')
        except:
            profile_link = ''
        return profile_link
    
    def reply_text(self,r):
        try:
            reply_text = r.find('div',{'data-sigil':'comment-body'}).text.replace('\n','').replace('\t','')
        except:
            reply_text = ''
        return reply_text
    
    def reply_time(self,r):
        try:
            reply_time = r.find('abbr').text
            reply_time = convert_time(reply_time)
        except:
            reply_time = ''    
        return reply_time
    

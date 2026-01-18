import time
import datetime
import os
import pandas as pd
import random
import instaloader
import json
import argparse
import mysql.connector

def query_posts(login_account):
    #comments >= 200 datetime 10-11 months
    mycursor.execute("""SELECT source,link FROM IG WHERE comments >= 200 AND date_time >= '2021-10-01'""")
    row = mycursor.fetchall()
    for r in row:
        source = r[0]
        link = r[1]
        Instragram(login_account).scrape_comments(source,link)

class Instragram:
    def __init__(self,login_account):
        self.login_account = login_account
    
    def scrape_comments(self,source,link):
        post_id = link.split('https://www.instagram.com/p/')[-1]
        try:
            post = instaloader.Post.from_shortcode(L.context, post_id)
            post_comments = post.get_comments()
            time.sleep(3)
            #迭代每則留言
            num = 1
            for comment in post_comments:
                comment_id = comment.id
                username = comment.owner.username
                created_date = comment.created_at_utc.strftime("%Y-%m-%dT%H:%M:%S")
                comment = comment.text
                insert_data = (source,link,comment_id,username,comment,created_date)
                print(insert_data)
                mycursor.execute(f"INSERT INTO ig_comment(source,link,comment_id,username,comment_text,comment_time) VALUES {insert_data}")
                mycursor.execute("""COMMIT;""")
                # if 留言 > 10,break
                if num >= comments_count:
                    break
                else:
                    num += 1
        except Exception as e:
            print(e)
            pass
        
if __name__ == '__main__':
    # CLI
    # run script,ex: python3 ig_scrape.py --account xxxxx --password xxxxx --limit 15
    parser = argparse.ArgumentParser(description="login IG account to scrape comments")
    parser.add_argument("--account",help="input account,EX: xxx@xxx.com",type=str)
    parser.add_argument("--password",help="input password",type=str)
    parser.add_argument("--limit",help="set comments conut,default is 10",default=10,type=int)
    
    args = parser.parse_args()
    account = args.account
    password = args.password
    comments_count = args.limit

    #connect database

    # read DB connection
    host = ""
    userName = ""
    port = ""
    password = ""
    dbName = ""

    # 讀取 JSON 設定檔
with open("db_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

    host = config["host"]
    userName = config["user"]
    port = config["port"]
    password = config["password"]
    dbName = config["database"]
    
    mydb = mysql.connector.connect(
        host=host,
        user=userName,
        port=port,
        password=password,
        database=dbName
    )

    mycursor = mydb.cursor()
    mycursor.execute("""START TRANSACTION;""")
    
    #login user account
    L = instaloader.Instaloader(user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0') 

    #從account list.txt選擇帳號
    login_account = L.login(account,password)
    query_posts(login_account)
        

import instaloader
import time
import datetime
import pandas as pd
from itertools import dropwhile, takewhile
import argparse
import mysql.connector
import os
import re

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="cdna1801",
  database="CDNA"
)
mycursor = mydb.cursor()
mycursor.execute("""START TRANSACTION;""")

def scrape_post(source,name_id,start_date,end_date,post_iterator):
    posts_data = []
    #setting scrape date range,date range is [2021-10-01,today]
    for post in takewhile(lambda p: p.date.strftime('%Y-%m-%d') > str(end_date), dropwhile(lambda p: p.date.strftime('%Y-%m-%d') > str(start_date), post_iterator)):
        try:
            post_id = post.shortcode
            post_date = post.date
            post_likes = post.likes
            post_comments = post.comments
            post_text = post.caption 
            
            link = 'https://www.instagram.com/p/'+post_id
            date_time = post_date.strftime('%Y-%m-%d')
            
            #寫資料到資料庫
            data = (source,date_time,link,name_id,post_likes,post_comments,post_text)
            write_to_database(data)
            print(data)
            
            #寫入csv檔案
            df = pd.DataFrame([{'source':source,
                                'post_id': post_id,
                                'post_date':post_date,
                                'post_likes':post_likes,
                                'post_comments':post_comments,
                                'post_text':post_text}])
            posts_data.append(df)
        except Exception as e:
            print(e)

    #沒有貼文就不寫入csv檔
    if posts_data == []:
        print('no post')
    else:
        write_to_csv(posts_data,name_id)

def write_to_csv(posts_data,name_id):
    #儲存成 csvfile
    df_save = pd.concat(posts_data, ignore_index=True)
    
    #沒有此路徑則自動建立
    folder_path = '/home/ftp_246/data_1/IG/'+time.strftime('%Y-%m')+'/post'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'{name_id}_posts_' + time.strftime('%Y%m%d')+ '.csv'
    df_save.to_csv(folder_path +'/'+ filename,encoding='utf-8-sig',index=0)

def write_to_database(data):
    #寫入資料到IG資料表
    try:
        mycursor.execute(f"""INSERT INTO IG(source,date_time,link,name_id,likes,comments,content) VALUES{data}""")
        mycursor.execute("COMMIT;")
    except Exception as e:
        print(e)
        pass

def main(account,password):
    #設定爬前2個月
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=60)  
    end_date = (start_date - months).strftime('%Y-%m-%d')

    L = instaloader.Instaloader(user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0')
    L.login(account,password)

    # 讀取IG清單,讀取欄位有source name_id end_date
    #清單在 網路輿情資料平台/各來源文章數量.xlsx
    df = pd.read_excel('Instagram_list.xlsx')
    for source,name_id in zip(df['source'],df['name_id']):
        try:
            profile = instaloader.Profile.from_username(L.context,name_id)
            post_iterator = profile.get_posts()
        except Exception as e:
            print(e)
            continue 
        #scrape posts
        scrape_post(source,name_id,start_date,end_date,post_iterator)

if __name__ == '__main__':
    #CLI Tool
    #輸入使用者帳號和密碼
    parser = argparse.ArgumentParser(description="login instagram account scrape comments")
    parser.add_argument("--account",help="input account EX: xxx@xxx.com",type=str)
    parser.add_argument("--password",help="input password",type=str)
    
    args = parser.parse_args()
    account = args.account
    password = args.password

    main(account,password)


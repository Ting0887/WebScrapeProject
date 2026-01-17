import scrapetube
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import datetime
import re
import os
import glob
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrape_youtubecomment import parse_ytcomment

# scrape channel videoid without rate limit by tool
def scrape_video_id(channel_name,channel_id,end_date):
    videos = scrapetube.get_channel(channel_id)
    save_videoid = []
    try:
        for video_id in videos:
            video_url = 'https://www.youtube.com/watch?v=' + video_id['videoId']
            res = requests.get(video_url)
            soup = BeautifulSoup(res.text,'lxml')
        
            # video date  and if date less than every month of 1
            try:
                video_date = soup.select_one('meta[itemprop="datePublished"][content]').attrs['content']
            except:
                continue
        
            if video_date < str(end_date):
                break
            else:
                save_videoid.append(video_url)
            print(video_url)
    except:
        pass
    
    if len(save_videoid) != 0:
        return save_videoid

#save data to txt file
def save_videoid_data(channel_name,result,videoid_path):
    #bulid folder yyyy-mm
    if not os.path.exists(videoid_path):
        os.makedirs(videoid_path)
    with open(videoid_path + channel_name + '_' + time.strftime('%Y%m%d')+'.txt','w',encoding='utf-8') as txtf:
        for videourl in result:
            txtf.write(videourl+'\n')
    txtf.close()
    
def read_videoid(videoid_path,videoinfo_path,comment_path,df):
    # 之後會調整清單路徑
    for channel_name in df['channel_name']:
        path = videoid_path + '*.txt'
        files = glob.glob(path)
        for file in files:
            if channel_name in file:
                print(channel_name)
                datalist = open(file).read().splitlines()              
                
                with ThreadPoolExecutor(max_workers=40) as executor:
                    future = executor.submit(scrape_ytinfo,channel_name,datalist,videoinfo_path)
                    future1 = executor.submit(scrape_ytcomment,channel_name,datalist,comment_path)
                '''
                work1 = Thread(target=scrape_ytinfo,args=(channel_name,datalist,videoinfo_path))
                work2 = Thread(target=scrape_ytcomment,args=(channel_name,datalist,comment_path))
                work1.start()
                work2.start()
                '''

# 預計存放位置, yyyy-mm/videoinfo/*.csv
def scrape_ytinfo(channel_name,datalist,videoinfo_path):   
    # write header
    header = ['channel_title','video_title','view_count','description',
               'publishAt','video_url','like_count','dislike_count']
    
    # if no dir,bulid dir
    if not os.path.exists(videoinfo_path):
        os.makedirs(videoinfo_path)
        
    with open(videoinfo_path + channel_name + '_videoinfo_' + time.strftime('%Y%m%d') + '.csv','a+',encoding='utf-8-sig') as csvf:
        w = csv.writer(csvf)
        w.writerow(header)
    
        for videourl in datalist:
            res = requests.get(videourl)
            soup = BeautifulSoup(res.text,'lxml')
            try:
                video_title = soup.find("meta",  property="og:title").attrs['content']
            except:
                video_title = ''
            try:
                view_count = soup.select_one('meta[itemprop="interactionCount"][content]').attrs['content']
            except:
                view_count = 0
            try:
                description = soup.find("meta",  property="og:description").attrs['content']
            except:
                description = ''
            try:
                publishAt = soup.select_one('meta[itemprop="datePublished"][content]').attrs['content']
            except:
                publishAt = ""
        
            likeAndDislike = soup(text=lambda t: '''"iconType":"LIKE"''' in t)
            try:
                like_count = re.findall('{"label":"\w.+人喜歡"',str(likeAndDislike))[0].split('"label":"')[-1].replace('人喜歡"','')
            except:
                like_count = 0
            try:
                dislike_count= re.findall('{"label":"\w.+人不喜歡"',str(likeAndDislike))[0].split('"label":"')[-1].replace('人不喜歡"','')
            except:
                dislike_count = 0
    
            w.writerow([channel_name,video_title,view_count,description,publishAt,videourl,like_count,dislike_count])

# 預計存放位置, yyyy-mm/comment/*.csv
def scrape_ytcomment(channel_name,datalist,comment_path):
    # if no dir,bulid dir
    if not os.path.exists(comment_path):
            os.makedirs(comment_path)
    csv_file = comment_path + channel_name + '_comment_' + time.strftime('%Y%m%d') + '.csv' 
    with open(csv_file , 'w',newline='',encoding='utf-8-sig') as csvf:
        w = csv.writer(csvf)
        w.writerow(['video_id','cid','text','time','author','channel','votes','photo','heart'])
        
    for videourl in datalist:
        id_num = videourl.split('/watch?v=')[-1]       
        # import scrape_youtubecomment.py parse_ytcomment function
        parse_ytcomment(id_num,csv_file)
        
def main(Nas_path,end_date,period):        
    #setting data path  
    videoid_path = Nas_path + '/' + time.strftime('%Y-%m') + '/video_id/'
    videoinfo_path = Nas_path + '/' + time.strftime('%Y-%m') + '/videoinfo/'
    comment_path = Nas_path + '/' + time.strftime('%Y-%m') + '/comment/'
      
    # read YT list
    #絕對路徑  
    df = pd.read_excel(dirpath+'/'+'Youtube_source_count.xlsx')
    for channel_name,channel_id in zip(df['source'],df['channel_id']):
        print(channel_name)
        result = scrape_video_id(channel_name,channel_id,end_date)
        if result == None:
            continue
        save_videoid_data(channel_name,result,videoid_path)
    
    read_videoid(videoid_path,videoinfo_path,comment_path,df)

if __name__ == '__main__':
    dirpath = os.path.dirname(os.path.abspath(__file__))
    Nas_path = '/home/ftp_246/data_1/Youtube'
    today = datetime.datetime.today()
    period = 31
    end_date = (today - datetime.timedelta(days=period)).strftime('%Y-%m-%d')
    main(Nas_path,end_date,period)    
    

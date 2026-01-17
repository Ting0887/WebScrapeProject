import requests
import os
import time
import datetime
from bs4 import BeautifulSoup
import json

def scrape_link(j):
    posts = []
    for item in j['items']:
        try:
            title = item['title']
            _id = item['id']
            category = item['categoryName']
            source = item['publisher']
            hash_id = item['url']['hash']
            date_time = datetime.datetime.fromtimestamp(int(item['publishTimeUnix'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            link = 'https://today.line.me/tw/v2/article/' + hash_id
            post = (title,_id,category,source,link,date_time)
            posts.append(post)
        except Exception as e:
            print(e)
            pass
    if len(posts)!=0:
        scrape_info(posts)

def scrape_info(posts):
    save_data = []
    for item in posts:
        #title id category source link date_time comment reply
        title = item[0]
        _id = item[1]
        category = item[2]
        source = item[3]
        link = item[4]
        date_time = item[5]

        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            content = soup.find('div','articleContent').text
        except:
            content = ''

        keyword = ''
        try:
            keywords = soup.find_all('div','exploreLinks-container')
            for k in keywords:
                keyword += k.text + ' '
        except:
            pass

        #scrape comment
        comment_data = []
        reply_data = []
        pivot = 0
        while True:
            comment_api = f'https://today.line.me/webapi/comment/list?articleId={_id}&sort=POPULAR&direction=DESC&country=TW&limit=60&pivot={pivot}&postType=Article'
            res = requests.get(comment_api)
            if res.json()['result']['comments']['comments'] == []:
                break
            for item in res.json()['result']['comments']['comments']:
                try:
                    comment_name = item['displayName']
                    comment_time = datetime.datetime.fromtimestamp(int(item['createdDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                    comment_text = ''
                    for c in item['contents']:
                        comment_text += c['extData']['content']
                        comment_data.append({'comment_name':comment_name,
                                             'comment_time':comment_time,
                                             'comment_text':comment_text})
                except Exception as e:
                    break
                pivot += 30

                #select reply link if reply !=0
                try:
                    reply_count = item['ext']['replyCount']
                except:
                    continue
                if reply_count != 0:
                    Sn = item['commentSn']
    
                    reply_link = f'https://today.line.me/webapi/comment/list?articleId={_id}&country=TW&limit=60&pivot=0&parentCommentSn={Sn}&postType=Article'
                    res = requests.get(reply_link)
                    if res.json()['result']['comments']['comments'] == []:
                        break
                    for item in res.json()['result']['comments']['comments']:
                        try:
                            reply_name = item['displayName']
                            reply_time = datetime.datetime.fromtimestamp(int(item['createdDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                            reply_text = ''
                            for c in item['contents']:
                                reply_text += c['extData']['content']
                            reply_data.append({'reply_name':reply_name,
                                               'reply_time':reply_time,
                                               'reply_text':reply_text})
                        except:
                            break
        
            save_data.append({'title':title,
                              'date_time':date_time,
                              'source':source,
                              'link':link,
                              'label':category,
                              'content':content,
                              'keyword':keyword,
                              'comment':comment_data,
                              'reply':reply_data})
    if len(save_data)!=0:
        write_to_json(save_data)

def write_to_json(save_data):
    folder_path = '/home/ftp_246/data_1/news_data/linetoday/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'linetoday_recommendation' + time.strftime('%Y%m%d%H')+'.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf8') as jf:
        json.dump(save_data,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    recom_url = 'https://today.line.me/webapi/api/v6/recommendation/articles/listings/mytoday_rec:id?offset=0&length=70&country=tw&gender=&age=&excludeNoThumbnail=0&containMainSnapshot=0'
    res = requests.get(recom_url)
    j = res.json()
    scrape_link(j)

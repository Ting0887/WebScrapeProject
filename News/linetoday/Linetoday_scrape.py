import os
import datetime
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, j):
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
        scrape_info(session, posts)

def scrape_info(session, posts):
    save_data = []
    for item in posts:
        #title id category source link date_time comment reply
        title = item[0]
        _id = item[1]
        category = item[2]
        source = item[3]
        link = item[4]
        date_time = item[5]

        res = session.get(link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            content = soup.find('div','articleContent').text
        except Exception:
            content = ''

        keyword = ''
        try:
            keywords = soup.find_all('div','exploreLinks-container')
            for k in keywords:
                keyword += k.text + ' '
        except Exception:
            pass

        #scrape comment
        comment_data = []
        reply_data = []
        pivot = 0
        while True:
            comment_api = f'https://today.line.me/webapi/comment/list?articleId={_id}&sort=POPULAR&direction=DESC&country=TW&limit=60&pivot={pivot}&postType=Article'
            res = session.get(comment_api, timeout=20)
            if res.json()['result']['comments']['comments'] == []:
                break
            for comment_item in res.json()['result']['comments']['comments']:
                try:
                    comment_name = comment_item['displayName']
                    comment_time = datetime.datetime.fromtimestamp(int(comment_item['createdDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                    comment_text = ''
                    for c in comment_item['contents']:
                        comment_text += c['extData']['content']
                    comment_data.append({'comment_name':comment_name,
                                         'comment_time':comment_time,
                                         'comment_text':comment_text})
                except Exception as e:
                    break
                pivot += 30

                #select reply link if reply !=0
                try:
                    reply_count = comment_item['ext']['replyCount']
                except Exception:
                    continue
                if reply_count != 0:
                    Sn = comment_item['commentSn']
    
                    reply_link = f'https://today.line.me/webapi/comment/list?articleId={_id}&country=TW&limit=60&pivot=0&parentCommentSn={Sn}&postType=Article'
                    res = session.get(reply_link, timeout=20)
                    if res.json()['result']['comments']['comments'] == []:
                        break
                    for reply_item in res.json()['result']['comments']['comments']:
                        try:
                            reply_name = reply_item['displayName']
                            reply_time = datetime.datetime.fromtimestamp(int(reply_item['createdDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                            reply_text = ''
                            for c in reply_item['contents']:
                                reply_text += c['extData']['content']
                            reply_data.append({'reply_name':reply_name,
                                               'reply_time':reply_time,
                                               'reply_text':reply_text})
                        except Exception:
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
    file_path = write_json_records(
        records=save_data,
        source_name='linetoday',
        category='recommendation',
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='linetoday',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    recom_url = 'https://today.line.me/webapi/api/v6/recommendation/articles/listings/mytoday_rec:id?offset=0&length=70&country=tw&gender=&age=&excludeNoThumbnail=0&containMainSnapshot=0'
    session = create_session()
    res = session.get(recom_url, timeout=20)
    j = res.json()
    scrape_link(session, j)

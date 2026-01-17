import re
import time
import datetime
def handle_likes(likes):
     if '萬' in likes:
         try:
             likes = int(float(re.findall(r'\d+\.\d+',likes)[0])*10000)
         except:
             likes =  int(re.findall(r'\d+',likes)[0])*10000
     elif '人' in likes:
         likes = int(re.findall(r'\d+',likes)[0])    
     else:
         likes = int(re.findall(r'\d+',likes)[0]) 
     return likes

def handle_comment(comment_count):
    if '萬' in comment_count:
        comment_count = int(float(comment_count[:-2])*10000)
    else:
        comment_count = int(re.findall(r'\d+',comment_count)[0])
    return comment_count

def handle_share(share_count):
     if '萬' in share_count:
         share_count = int(float(share_count[:-2])*10000)
     else:
         share_count = int(re.findall(r'\d+',share_count)[0])
     return share_count

def handle_posttime(post_time):
    if post_time == '':
        post_time == ''

    elif '年' in post_time:
        d = re.findall(r'\d+',post_time)
        post_time = datetime.date(int(d[0]),int(d[1]),int(d[2]))
        post_time = post_time.strftime('%Y年%m月%d日')
    elif '分'  in post_time:
        post_time = time.strftime('%Y年%m月%d日')
    elif '時'  in post_time:
        post_time = time.strftime('%Y年%m月%d日')
    elif '天'  in post_time:
        post_time = time.strftime('%Y年%m月%d日')
    elif '秒' in post_time:
        post_time = time.strftime('%Y年%m月%d日')
    elif '昨' in post_time:
        post_time = time.strftime('%Y年%m月%d日')

    elif '年' not in post_time:
        try:
            post_time = time.strftime('%Y年') + post_time
            d = re.findall(r'\d+',post_time)
            post_time = datetime.date(int(d[0]),int(d[1]),int(d[2]))
            post_time = post_time.strftime('%Y年%m月%d日')
        except:
            post_time = ''
    
    else:
        post_time = time.strftime('%Y年%m月%d日')
   
    return post_time
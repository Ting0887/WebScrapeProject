import datetime
import time
import re

# week data
week_data = ['一','二','三','四','五','六','日']
# sec min hour
short_data = ['秒','分','時']

def convert_time(comment_time):
    #秒 分 時 are regarded as today
    if comment_time[-1] in short_data:
        date_num = re.findall(r'\d+',comment_time)[0]
        comment_time = (datetime.datetime.today() - datetime.timedelta(seconds=int(date_num))).strftime('%Y-%m-%d')
        
    # 上星期、上週    
    elif (comment_time.startswith('上星期') or\
          comment_time.startswith('上週')) and\
          comment_time[-1] in week_data:    
              comment_time = (datetime.datetime.today() - datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')
    # this week
    elif comment_time[-1] in week_data:
        num = week_data.index(comment_time[-1])
        today = datetime.datetime.today()
        offset = (today.weekday() - num) % 7
        comment_time = (today - datetime.timedelta(days=offset)).strftime('%Y-%m-%d')

    # few weeks ago      
    elif comment_time.endswith('週'):
        date_num = re.findall(r'\d+',comment_time)[0]
        comment_time = (datetime.datetime.today() - datetime.timedelta(weeks=int(date_num))).strftime('%Y-%m-%d')
        
    # few months ago              
    elif comment_time.endswith('月'):
        date_num = re.findall(r'\d+',comment_time)[0]
        comment_time = (datetime.datetime.today() - datetime.timedelta(days=30*int(date_num))).strftime('%Y-%m-%d')
    
    # few years ago                    
    elif comment_time.endswith('年'):
        date_num = re.findall(r'\d+',comment_time)[0]
        comment_time = (datetime.datetime.today() - datetime.timedelta(weeks=52*int(date_num))).strftime('%Y-%m-%d')
                
    else:
        comment_time = time.strftime('%Y-%m-%d')
    return comment_time


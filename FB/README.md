# FB_fanspage
## install
* pip install selenium
## how to use?
* git clone https://github.com/Ting0887/FB_fanspage
* download chromedriver https://chromedriver.chromium.org/
## extract post
```
from fb_extract_post import FB_crawler

driverPath = 'your path'
FB_URL = 'https://m.facebook.com/xxx'
account = 'your account'
password = 'your password'
file_name = 'your file name' 
end_date = 'format : yyyy-mm-dd' ex. '2021-01-01'

FB = FB_crawler(driverPath,FB_URL,account,password,file_name,end_date)
FB.scroll_down()

```
## extract comment
```
from fb_extract_comment import FB_Crawler
driverPath = 'your chromedriver path'
        
account = 'your account'
password = 'your password'
post_URL = 'add mobile post url'
comment_limit = 'set comment limit<int>' ex. 100
output_file = 'your file name' ex. test

FB = FB_Crawler(driverPath,account,password,post_URL,comment_limit,output_file)
FB.scroll_down()
```


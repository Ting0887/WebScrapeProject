import instaloader
import time
import datetime
import pandas as pd
#save posts
article = []

L = instaloader.Instaloader()
L.login("", "")
#透過文章 id "CGMTbf_lTIa" 取得post物件
post = instaloader.Post.from_shortcode(L.context, "CGMTbf_lTIa")
post_comments = post.get_comments()
#迭代每則留言
for comment in post_comments:
    post_id = comment.id
    username = comment.owner.username
    created_date = comment.created_at_utc.strftime("%Y-%m-%dT%H:%M:%S")
    comment = comment.text
    print(post_id, username, created_date,comment)
    df = pd.DataFrame([{'post_id': post_id,
                        'username':username,
                        'created_date':created_date,
                        'comment':comment}])
    article.append(df)

df_save = pd.concat(article, ignore_index=True)
df_save.to_excel('test.xlsx',index=0)
    
    

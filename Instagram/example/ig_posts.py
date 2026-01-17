import instaloader
import time
import datetime
import pandas as pd
article = []
L = instaloader.Instaloader() 
#add ig account
L.login("", "")
profile = instaloader.Profile.from_username(L.context, "tsai_ingwen")
#取得post迭代物件
post_iterator = profile.get_posts()
#迭代post_iterator 取得 post
for post in post_iterator:
    print(post)
    post_id= post.shortcode
    post_likes = post.likes
    post_comments = post.comments
    post_text = post.caption #pcaption只會給前段內文，如果要完整內文用caption 
    df = pd.DataFrame([{'post_id': post_id,
                        'post_likes':post_likes,
                        'post_comments':post_comments,
                        'post_text':post_text}])
    article.append(df)

df_save = pd.concat(article, ignore_index=True)
df_save.to_excel('test_posts.xlsx',index=0)


    
import instaloader
L = instaloader.Instaloader() 
#登入ig帳號，部分操作會需要登入帳號，由於取得追蹤數貼文數不需要登入，這步驟省略
L.login("", "")
#取得目標ig帳號的profile物件
profile = instaloader.Profile.from_username(L.context, "tsai_ingwen")
#從profile物件取得追蹤數
followers=profile.followers
#從profile物件取得貼文數
post_count=profile.get_posts().count
#從profile物件取得自介
biography=profile.biography
print("Tsia has {} followers".format(followers))
print("Tsia has {} posts".format(post_count))
print(biography)
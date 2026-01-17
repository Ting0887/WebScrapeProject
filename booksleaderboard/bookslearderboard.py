def showkind(url,kind):
    html = requests.get(url,headers=headers).text
    soup = BeautifulSoup(html,'html.parser')
    try:
        pages=int(soup.select('.cnt_page span')[0].text)
        print("共有",pages,"頁")
        for page in range(1,pages+1):
            pageurl = url + '&page=' + str(page).strip()
            print("第",page,"頁",pageurl)
            showpage(pageurl,kind)
    except:
        showpage(url,kind)
        
def showpage(url,kind):
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html,'html.parser')
    #近期新書、在class="mod type02_m012 clearfix"中
    res = soup.find_all('div',{'class':'mod type02_m012 clearfix'})[0]
    items = res.select('.item')
    n = 0
    for item in items:
        msg = item.select('.msg')[0]
        src = item.select('a img')[0]["src"]
        title = msg.select('a')[0].text
        imgurl = src.split("?i=")[-1].split("&")[0]
        author = msg.select('a')[1].text
        publish = msg.select('a')[2].text
        date = msg.find('span').text.split(":")[-1]
        onsale = item.select('.price .set2')[0].text
        content = item.select('.txt_cont')[0].text.replace(" ","").strip()
        print("\n分類:" + kind)
        print("圖片網址:" + imgurl)
        print("作者:" + author)
        print("出版社:" + publish)
        print("出版日期:" + date)
        print("內容:" + content)
        listdata = [kind,title,imgurl,author,publish,date,onsale,content]
        list1.append(listdata)
        n += 1
        print("n=",n)
        #if n==2: break #開發階段
        
def twobyte(kindno):
    if kindno<10:
        kindnostr = "0" + str(kindno)
    else:
        kindnostr=str(kindno)
    return kindnostr

def auth_gss_client(path,scopes): #建立憑證
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path,scopes)
    return gspread.authorize(credentials)

import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
auth_json_path = 'stable-healer-242603-5c3e72b98a1c.json' #json金鑰
gss_scopes = ['https://spreadsheets.google.com/feeds']
gss_client = auth_gss_client(auth_json_path, gss_scopes) #連線

spreadsheets_key = '1oLPVOH7AEeAujp4stkPtDb6pN6UPKWKv7nMP4cyHSkg'
sheet = gss_client.open_by_key(spreadsheets_key).sheet1
#sheet.claer()

list1 = []

kindno = 1 #要下載的分類，預設為第一類，文學小說
homeurl = "https://www.books.com.tw/web/books_nbtopm_01?o=5&v=1"
mode = "?o=5&v=1"
url = "https://www.books.com.tw/web/books_nbtopm_"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
html = requests.get(homeurl,headers=headers).text
soup = BeautifulSoup(html,'html.parser')

res = soup.find('div',{'class':'mod_b type02_l001-1 clearfix'})
hrefs = res.select('a')

kindno = int(input("請輸入要下載的分類:"))
if 0 < kindno <= len(hrefs):
    kind = hrefs[kindno-1].text
    print("下載的分類編號:{} 分類名稱:{}".format(kindno,kind))
    
    kindurl = url + twobyte(kindno) + mode
    print(kindurl)
    showkind(kindurl,kind)
    
    #儲存Google試算表
    print('資料寫入雲端google試算表中...')
    listtitle = ['分類','書名','圖片網址','作者','出版社','出版日期','優惠價','內容']
    sheet.append_row(listtitle) #標題
    for item1 in list1:
        sheet.append_row(item1)
        sleep(1) #必須加上適當的delay
    
else:
    print("分類不存在")
print('資料儲存完畢')
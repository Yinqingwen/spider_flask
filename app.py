from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
from werkzeug.datastructures import Range

app = Flask(__name__)

#此处为免翻墙地址，应注意被屏蔽情况
BaseUrl = 'https://cl.5837x.xyz'
proxy = '127.0.0.1:50461' #'192.168.11.134:50461'
proxies = {
    'http': 'http://' + proxy,
    'https': 'https://' + proxy
}

#获取相应的网页内容函数
def GetPage(url):
    res = requests.get(url,verify=False)
    #将网页编码强制设置为GBK
    res.encoding = "gbk"
    #获取网页内荣并返回
    return BeautifulSoup(res.text)

#获取论坛下最大页数
def GetMaxNumber(number):
    #以/分割页面数量
    temp = str(number).split('/')
    #返回最大页面数量
    return int(temp[1])

@app.route("/")
def home():
    #此处为免翻墙地址，应注意被屏蔽情况  
    url = "{}/{}".format(BaseUrl,'index.php')
    #获取首页内容
    soup = GetPage(url)
    page_list=[]
    #获取首页上所有论坛信息
    for link in soup.find_all('tr',attrs={'class': 'tr3 f_one'}):
        url = link.th.h2.a['href']
        start = link.th.h2.a['href'].find('=') + 1
        number = int(url[start:])
        #创建字典，用于传递论坛信息
        page_list.append( {'number': number,'title': link.th.h2.a.text,'detail': link.th.span.text} )

    return render_template("index.html",page_list = page_list)

#获取书籍数据
def GetBookInfo(title,span_list):
    #创建数据列表
    bookinfo = dict()
    #书目名称
    bookinfo['Title'] = title
    for span in span_list:
        links = span.find_all('a')
        for link in links:
            continue
        temp = link['href'].split('?')[1]
        temp1 = temp.split('&')
        #书目ID
        bookinfo['Id'] = int(temp1[0].split('=')[1])
        #书目页数
        bookinfo['Number'] = int(temp1[1].split('=')[1])
    return bookinfo

@app.route("/page/<int:number>")
def page(number):
    #根据论坛编号获取论坛信息
    url = "{}/thread0806.php?fid={}".format(BaseUrl,number)
    #获取论坛页面
    soup = GetPage(url)
    #获取该论坛总页数
    maxnumber = GetMaxNumber(soup.find('a',attrs={'class': 'w70'}).input['value'])
    #定义文章列表
    articles=[]
    for x in range(maxnumber):
        ArticlesUrl = "{}&search=&page={}".format(url,x+1)
        soup = GetPage(ArticlesUrl)
        tbody = soup.find('tbody',attrs={'id': 'tbody'})
        trs = tbody.find_all('tr',attrs={'class': 'tr3 t_one tac'})
        for tr in trs:
            #获取书目名称
            title = tr.h3.a.text
            tspans = tr.find_all('span',attrs={'style': 'font-size:7pt;font-family:verdana;'})
            #获取书目列表
            bookinfo = GetBookInfo(title,tspans)
            articles.append(bookinfo)
    
    return render_template('booklist.html', articles = articles)
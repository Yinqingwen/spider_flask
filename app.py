from typing import Pattern
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import re
from werkzeug.datastructures import Range

app = Flask(__name__)

#地址发布页
PublishPage = 'http://www.gfqzkep.com/'
BaseUrls = []
BaseURL= ''

#获取发布页所列出的地址
def GetPublishPages():
    #此处为免翻墙地址列表
    global BaseUrls
    #地址基础
    BaseAddress = ['x', 'y', 'z']
    #获取发布页内容
    res = requests.get(PublishPage)
    #检测获取结果
    if (res.status_code == 200):
        #将网页代码设置为utf-8
        res.encoding = "utf-8"
        #解析网页内容
        soup = BeautifulSoup(res.text,'lxml')
        #获取JS脚本
        scripttext = soup.select("body script")
        #获得域名基础部分
        urltext = re.findall(r"dn = \'(.+)\'", str(scripttext))[0]
        #获取免翻墙地址列表
        for base in BaseAddress:
            #依据基础规则生成免翻墙地址
            baseurl = "https://cl.{}{}.xyz".format(urltext,base)
            #加入地址列表中
            BaseUrls.append(baseurl)
    else:
        #报错
        print('访问发布页错误，请检查！！！')

#获取网站首页函数
def GetUrl():
    global BaseUrls
    global BaseURL

    if (BaseUrls == []):
        GetPublishPages()
    for baseurl in BaseUrls:
        res = requests.get(baseurl)
        if (res.status_code == 200):
            BaseURL = baseurl
            break

#获取相应的网页内容函数
def GetPage(url):
    res = requests.get(url,verify=False)
    #将网页编码强制设置为GBK
    res.encoding = "utf-8"
    #获取网页内荣并返回
    return BeautifulSoup(res.text, features="lxml")

#获取论坛下最大页数
def GetMaxNumber(number):
    #以/分割页面数量
    temp = str(number).split('/')
    #返回最大页面数量
    return int(temp[1])

#获取每个论坛的页面数量
def GetPageNumber(BaseUrl, number):
    #根据论坛编号获取论坛信息
    url = "{}/thread0806.php?fid={}".format(BaseUrl,number)
    #获取论坛页面
    soup = GetPage(url)
    #获取该论坛总页数
    pagenumber = 0
    pagecontor = ''
    try:
        pagecontor = soup.find('a',attrs={'class': 'w70'}).input['value']
    except:
        pagecontor = '0/0'
    
    pagenumber = GetMaxNumber(pagecontor)
    return pagenumber

#首页
@app.route("/")
def home():
    global BaseURL
    page_list=[]
    #首先获取发布页地址列表
    GetUrl()
    url = "{}/{}".format(BaseURL,'index.php')
    #获取首页内容
    soup = GetPage(url)
    
    #获取首页上所有论坛信息
    for link in soup.find_all('tr',attrs={'class': 'tr3 f_one'}):
        url = link.th.h2.a['href']
        start = link.th.h2.a['href'].find('=') + 1
        number = int(url[start:])
        #创建字典，用于传递论坛信息
        page_list.append( {'number': number,'title': link.th.h2.a.text,'detail': link.th.span.text,"pagenumber": 0} )
    #准备获取每个论坛的页数
    for page in page_list:
        page['pagenumber'] = GetPageNumber(BaseURL,page['number'])
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

#论坛版块
@app.route("/board/<int:number>/<int:pagenumber>")
def board(number,pagenumber):
    #定义文章列表
    articles=[]
    global BaseURL
    print(BaseURL)
    #根据论坛编号获取论坛信息
    url = "{}/thread0806.php?fid={}&search=&page={}".format(BaseURL,number,pagenumber)
    #获取论坛页面
    soup = GetPage(url)

    tbody = soup.find('tbody',attrs={'id': 'tbody'})
    trs = tbody.find_all('tr',attrs={'class': 'tr3 t_one tac'})
    for tr in trs:
        print(tr)
    """
            #获取书目名称
            title = tr.h3.a.text
            tspans = tr.find_all('span',attrs={'style': 'font-size:7pt;font-family:verdana;'})
            #获取书目列表
            bookinfo = GetBookInfo(title,tspans)
            articles.append(bookinfo)
    """
    return render_template('booklist.html', articles = articles)
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
    #返回子论坛信息
    return render_template("index.html",page_list = page_list)

#获取书籍数据
#title-内容题目
#span-list 页数列表
def GetContentInfo(BoardId,tr):
    #创建数据列表
    Contentinfo = dict()
    #定义变量
    ContentTitle = ''   #内容标题
    ContentId = 0       #内容ID
    ContentPage = 0     #内容页数，默认为1
    #内容名称
    ContentTitle = tr.h3.a.text
    tspans = tr.find_all('span',attrs={'style': 'font-size:7pt;font-family:verdana;'})
    if (tspans == []):
        #只有一页内容
        #获取内容url
        contenturl = tr.h3.a['href']
        urltext = re.findall(r"\/(.+).html", str(contenturl))[0]
        ContentId = str(urltext.split('/')[2])
        ContentPage = 1
    else:
        #获取页数
        for span in tspans:
            links = span.find_all('a')
            #获取最后页数
            for link in links:
                continue
            temp = link['href'].split('?')[1]
            temp1 = temp.split('&')
            #内容ID
            ContentId = int(temp1[0].split('=')[1])
            #内容页数
            ContentPage = int(temp1[1].split('=')[1])

    Contentinfo['BoardId'] = BoardId
    Contentinfo['Title'] = ContentTitle
    Contentinfo['Id'] = ContentId
    Contentinfo['Number'] = ContentPage

    #返回内容信息
    return Contentinfo

#论坛版块
#number 子论坛编号
#pagenumber 页数编号
@app.route("/board/<int:number>/<int:pagenumber>")
def board(number,pagenumber):
    #定义文章列表
    articles=[]
    global BaseURL
    #如果基本地址为空，获取地址
    if (BaseURL == ''):
        GetUrl()
    #根据论坛编号获取论坛信息
    url = "{}/thread0806.php?fid={}&search=&page={}".format(BaseURL,number,pagenumber)
    #获取论坛页面
    soup = GetPage(url)
    #获取内容名称
    tbody = soup.find('tbody',attrs={'id': 'tbody'})
    trs = tbody.find_all('tr',attrs={'class': 'tr3 t_one tac'})
    for tr in trs:
        articles.append(GetContentInfo(number,tr))

    return render_template('contentlist.html', articles = articles)

#https://cl.2062x.xyz/htm_data/2201/20/4651187.html
#https://cl.2062x.xyz/read.php?tid=4855913&page=1&fpage=1
#显示书籍
@app.route("/Display/<int:BoardId>/<int:Id>/<int:Number>")
def Display(BoardId,Id,Number):
    global BaseURL
    if (BaseURL == ''):
        GetUrl()
    if (Id <= 0):
        return '书籍编号错误！！！'
    
    for page in range(Number):
        url = "{}/read.php?tid={}&page={}&fpage=1".format(BaseURL,Id,page+1)
        soup = GetPage(url)
        print(soup)
    
    return 'DisplayBook'
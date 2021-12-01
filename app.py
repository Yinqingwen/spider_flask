from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route("/")
def home():
    """获取免翻墙地址"""  
    url = "https://cl.5837x.xyz/index.php/"
    res = requests.get(url,verify=False)
    """将网页编码强制设置为GBK"""
    res.encoding = "gbk"
    soup = BeautifulSoup(res.text)
    for link in soup.find_all('a'):
        print(link.get())
    site_list = [1,2,3,4]
    return render_template("index.html",site_list = site_list)
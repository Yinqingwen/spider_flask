from flask import Flask
import requests
from requests.packages import urllib3

app = Flask(__name__)
urllib3.disable_warnings()

@app.route("/")
def home():  
    req = requests.get('https://grwsyw.bjgjj.gov.cn/ish/',verify=False)
    print(req.text)
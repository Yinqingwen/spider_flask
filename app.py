from flask import Flask
import requests
from requests.models import Response
from requests.packages import urllib3

app = Flask(__name__)
urllib3.disable_warnings()

@app.route("/")
def home():  
    url = "https://cl.3637x.xyz/index.php"
    response1 = requests.get(url)
    return 'response1'     
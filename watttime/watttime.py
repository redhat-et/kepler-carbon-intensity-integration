import requests
from requests.auth import HTTPBasicAuth
from dotenv import dotenv_values
import os

dirname = os.path.dirname
config = dotenv_values(os.path.join(dirname(dirname(__file__)), '.env'))
rsp = requests.get(config["LOGIN_URL_WATTTIME"], auth=HTTPBasicAuth(config["WATTTIME_USERNAME"], config["WATTTIME_PASSWORD"]))
print(rsp.json())


import os
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from flask import Flask,jsonify
import time
import random
import json

PROXY_HOST = "premium-residential.geonode.com"
PROXY_PORT = "9000"
PROXY_USER = "geonode_PICQT8eL6y-country-IN"
PROXY_PASS = "433c7916-131a-4fbd-98f6-fdaa3311e3b2"

URL = 'https://google.com/search?q=online+casino'
domains = ["vocanospin.com","crcsix.in"]

app = Flask(__name__)

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 3,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "webRequest",
        "webRequestAuthProvider"
        ],
    "host_permissions": [
        "<all_urls>"
    ],
    "background": {
        "service_worker": "background.js"
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = Options()

    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(executable_path= r"/usr/bin/chromedriver/",options=chrome_options)
    return driver

@app.get("/")
def main():
    retry = 3
    search_domain = ''

    while retry>0:
        try:
            driver,ip_dict = get_ip()            
            driver.get(URL)
            search_domain = random.choice(domains)
            search_url = driver.find_element(By.XPATH,"//span[contains(text(),'"+search_domain+"')]")
            domain = search_url.text
            print(f"Domain: {search_domain}")            
            search_url.click()
            driver.implicitly_wait(random.randint(3,7))
            return {"domain":domain,"ip":ip_dict["ip"],"region":ip_dict["region"]}
        except:
            print(f'{search_domain} not found, retrying with different domain')
            retry -=1

    return jsonify({"Error":"site does not responding,please try again"})

def get_ip():
    ip_url = 'https://ipinfo.io/json'
    chrome = get_chromedriver(use_proxy=True)
    chrome.get(ip_url)
    ip_json = chrome.find_element(By.TAG_NAME,"pre")
    ip = json.loads(ip_json.text)

    print(f"IP: {ip['ip']} Region: {ip['region']}")
    return chrome,ip

if __name__ == '__main__':
    main()
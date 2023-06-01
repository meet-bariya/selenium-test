from flask import Flask,jsonify,render_template
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import seleniumwire.undetected_chromedriver as uc
import random
import json

domains = ["vocanospin.com","crcsix.in"]
URL = 'http://www.google.com/search?q=online+casino'

app = Flask(__name__)

def driver_init():
    options = {
    'proxy':
    {
        'http':'http://geonode_pFUH03TpuV-country-IN:1ac4e997-7115-4a93-b0f0-a0f5a8e7666d@premium-residential.geonode.com:9000',
        'https':'https://geonode_pFUH03TpuV-country-IN:1ac4e997-7115-4a93-b0f0-a0f5a8e7666d@premium-residential.geonode.com:9000',
    }
}

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(seleniumwire_options=options,options=chrome_options)
    return driver

@app.get('/')
def google_search():

    retry = 2
    search_domain = ''
    
    while retry>0:
        try:
            chrome,ip_dict = get_ip()
            chrome.get(URL)
            chrome.implicitly_wait(4)
            search_domain = random.choice(domains)

            wait = WebDriverWait(chrome, 30)
            search_url = wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"//span[contains(text(),'"+search_domain+"')]")))
            domain = search_url.text
            print(f"Domain: {search_domain}")
            
            search_url.click()
            chrome.implicitly_wait(random.randint(2,5))
            chrome.close()
            return {"domain":domain,"ip":ip_dict["ip"],"region":ip_dict["region"]}
        except:
            print(f'{search_domain} not found, retrying with different domain')
            retry -=1

    return jsonify({"Error":"site does not responding,please try again"}),404

@app.route('/proxy_ip')
def get_ip():
    ip_url = 'https://ipinfo.io/json'
    chrome = driver_init()
    chrome.get(ip_url)
    ip_json = chrome.find_element(By.TAG_NAME,"pre")
    ip = json.loads(ip_json.text)

    print(f"IP: {ip['ip']} Region: {ip['region']}")
    return chrome,ip

if __name__ == "__main__":
    app.run(debug=True)
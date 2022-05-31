from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tld import get_fld
from PIL import Image
from datetime import datetime
import time
import json
import sys, getopt
import requests

def check_TLS(URL):

    try:
        response = requests.get(URL)
        return False
    except requests.exceptions.RequestException as e:
        return True

accept_words_list = set()            # add the txt list as a set
for w in open("accept_words.txt", "r").read().splitlines():
    if not w.startswith("#") and not w == "":
            accept_words_list.add(w)

url='https://wrong.host.badssl.com/'
check_TLS(url)
if check_TLS==True:
    print ("TLS error")
else:
    driver = webdriver.Chrome("./chromedriver")
    website_visit={} # dictionary for generating the json for each website visit
    website_visit['pageload_start_ts'] = time.time() # start time 

    driver.get(url)
    website_visit['pageload_end_ts']=time.time()
    time.sleep(5)

    website_visit['post_pageload_url'] = driver.current_url   #loaded the url
    website_visit['domain'] = get_fld(url)  # the domain of every website
    website_visit['crawl_mode']="desktop"  # need to be changed later to desktop or mobile

    contents = driver.find_elements_by_css_selector("a, button, div, span, form, p")

    candidate = None
    screen=website_visit['domain']  + "_m_desktop_pre_consent.png"

    driver.save_screenshot(screen) # taking the secreenshot before accepting

    for c in contents:
        try: # print(c.text.lower().strip(" ✓›!\n"))
                if c.text.lower().strip(" ✓›!\n") in accept_words_list:
                    candidate = c  
                    break
        except:
            website_visit['consent_status']="errored"

                        
        # Click the candidate
    if candidate is not None:
        try: 
            candidate.click()
            website_visit['consent_status']="clicked"
        except:
            website_visit['consent_status']="errored"
    else:
        website_visit["consent_status"]="not_found"

    time.sleep(5)
    screen=website_visit['domain']  + "_m_desktop_post_consent.png"
    driver.save_screenshot(screen) # taking the secreenshot after  accepting the cookies

    req_response=list()

    for request in driver.requests:
        req_resp={}
        req_resp['request_url']=request.url
        if (request.response is not None):
            req_resp['timestamp']=request.response.headers['date']
        req_headers={}
        for header in request.headers:
            req_headers[header]=request.headers[header][0:512]
        req_resp['request_headers']=req_headers
        if (request.response is not None):
            resp_headers={}
            for response in request.response.headers:
                resp_headers[response]=request.response.headers[response][0:512]
            req_resp['response_headers']=resp_headers
        req_response.append(req_resp)

    website_visit['requests']=req_response
        

    file_name=website_visit['domain'] + '.json'

    with open(file_name, 'w') as out:
        json.dump(website_visit, out,indent=4)
    driver.quit()



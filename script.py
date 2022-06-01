# -*- coding: utf-8 -*-
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tld import get_fld
from PIL import Image
from datetime import datetime
import time
import json
import sys, getopt
import requests
import argparse
import csv

from error_handler import ErrorHandler

## Crawler desktop and mobile // DONE
## Headless // DONE
## Logs
## Logs accept button success
## Global timeout value
## Screenshot names change for mobile and desktop // DONE
## Handle domains that do not exist //a //DONE
## Page load errors //a //DONE
## Add all variables needed for the analysis // DONE (yesterday itself?)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m','--isMobile',type=str,choices=['mobile','desktop'])
    parser.add_argument('-u','--singleURL',type=str)
    parser.add_argument('-i','--csvFileUrl',type=str)
    parser.add_argument('-head','--isHeadless',type=str,default='headfull',choices=['headless','headfull'])
    parsed_stuff = parser.parse_args()
    urls = []

    successful_clicks_count = 0 
    errored_clicks_count = 0
    not_found_clicks = []
    isMobile = True if parsed_stuff.isMobile == 'mobile' else False
    isHeadless = True if parsed_stuff.isHeadless == 'headless' else False

    def build_url():
        if parsed_stuff.singleURL != None:
            urls.append(parsed_stuff.singleURL)
        if parsed_stuff.csvFileUrl != None:
            with open(parsed_stuff.csvFileUrl) as file:
                data = csv.reader(file,delimiter=',')
                for url_data in data:
                    url_data_str = url_data[1]
                    if not url_data_str.startswith("http://") and not url_data_str.startswith("https://"):
                        url_data_str = "http://www." + url_data_str
                    urls.append(url_data_str)
        urls.remove('http://www.domain')

    build_url()

    def configure_driver():
        webdriver_options = webdriver.ChromeOptions()
        if isMobile:    
            webdriver_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
        if isHeadless:
            webdriver_options.add_argument('--headless')
        driver = webdriver.Chrome("./chromedriver",chrome_options = webdriver_options)
        user_agent = driver.execute_script("return navigator.userAgent;")
        print(user_agent)
        return driver

    def get_screenshot_name(domain: str, type:str):
        return domain+'_'+parsed_stuff.isMobile+type+'.png'

        
    def check_TLS(URL):                                         # TLS error
        try:
            response = requests.get(URL)
            return False
        except requests.exceptions.RequestException as e:
            if 'CERTIFICATE_VERIFY_FAILED' in str(e):
                print('TLS_error')
            elif 'hostname' in str(e):
                print('TLS_error')
            return True

    def time_out(url):                              # timeout error code 
        try:
            driver.set_page_load_timeout(30)
            driver.get(url)
        except TimeoutException as e:
            print('time_out')
            driver.quit()

    def domain_not_exit(url):      # domian does not exit we do not need this in anaylsis report
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as e:
                print('domain_does_not_exit')
                driver.quit()

    stripped_urls = urls[0:2]
    accept_words_list = set()            # add the txt list as a set
    for w in open("accept_words.txt", "r").read().splitlines():
        if not w.startswith("#") and not w == "":
                accept_words_list.add(w)

    print(stripped_urls)
    stripped_urls = ['http://expried.badssl.com']
    for url in stripped_urls: 
        driver = configure_driver()
        error_handler = ErrorHandler(driver,url)
        
        if error_handler.error_counter > 0:
            print("************************* error count************ "+ str(error_handler.error_counter))
            driver.quit()
        else:    
            website_visit={} # dictionary for generating the json for each file
            website_visit['pageload_start_ts'] = time.time() # start time 
            driver.get(url)
            website_visit['pageload_end_ts']=time.time()
            time.sleep(10)
            website_visit['post_pageload_url'] = driver.current_url   #loaded the url
            website_visit['domain'] = get_fld(url)  # the domain of every website
            website_visit['crawl_mode']= 'mobile' if isMobile == True else 'desktop'  # need to be changed later to desktop or mobile

            contents = driver.find_elements_by_css_selector("a, button, div, span, form, p")

            candidate = None
            screen_shot_name = get_screenshot_name(website_visit['domain'],'_pre_consent') 
            print(screen_shot_name)
            driver.save_screenshot(screen_shot_name) # taking the secreenshot before accepting

            for c in contents:
                try: 
                    if c.text.lower().strip(" ✓›!\n") in accept_words_list:
                        candidate = c  
                        break
                except:
                    website_visit['consent_status']="errored"
                    errored_clicks_count = errored_clicks_count + 1           
            # Click the candidate
            if candidate is not None:
                try: 
                    candidate.click()
                    website_visit['consent_status']="clicked"
                    successful_clicks_count = successful_clicks_count + 1
                except:
                    website_visit['consent_status']="errored"
                    errored_clicks_count = errored_clicks_count + 1
            else:
                website_visit["consent_status"]="not_found"
                not_found_clicks.append(url)

            time.sleep(10)
            screen_shot_name_post = get_screenshot_name(website_visit['domain'],'_post_consent')
            print(screen_shot_name_post)
            driver.save_screenshot(screen_shot_name_post) # taking the secreenshot after  accepting the cookies

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

if __name__ == "__main__":
    main()

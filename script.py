# -*- coding: utf-8 -*-
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from tld import get_fld
import time
import json
import argparse
import csv
from UniversalLogger import UniversalLogger
from error_handler import ErrorHandler

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
    logger = UniversalLogger(isMobile)

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
            webdriver_options.add_argument('--user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/101.0.4951.44 Mobile/15E148 Safari/604.1"')
           #webdriver_options.add_argument('window-size=500,500')
        if isHeadless:
            webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--no-sandbox')
        webdriver_options.add_argument('--disable-gpu')
        webdriver_options.add_argument('--dns-prefetch-disable')
        webdriver_options.add_argument('--log-level=3')
        #webdriver_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome("./chromedriver",chrome_options = webdriver_options)
        #user_agent = driver.execute_script("return navigator.userAgent;")
        return driver

    def get_screenshot_name(domain: str, type:str):
        return domain+'_'+parsed_stuff.isMobile+type+'.png'
        
    #stripped_urls = urls[0:1]
    accept_words_list = set()            # add the txt list as a set
    for w in open("accept_words.txt", "r").read().splitlines():
        if not w.startswith("#") and not w == "":
                accept_words_list.add(w)

    def try_clicking_button_with_script(driver):
        element = driver.find_elements(by=By.CSS_SELECTOR,value="a, button, div, span, form, p") 
        driver.execute_script("arguments[0].click();",element)

    stripped_urls_2 = ['http://www.netflix.net']
    stripped_urls = ['http://www.so.com','http://www.www.gov.uk','http://www.cloudfront.net','http://www.wa.me',' http://www.ytimg.com','http://www.forms.gle','http://www.hao123.com', 'http://expired.badssl.com']
    
    for url in stripped_urls_2: 
        driver = configure_driver()
        error_handler = ErrorHandler(driver,url,logger,isMobile)
        
        if error_handler.error_counter > 0:
            logger.dump_json()
            print("************************* error count ************ "+ str(error_handler.error_counter))
            driver.quit()
        else:   
            print('##################### Entering else block, no errors ################') 
            website_visit={} # dictionary for generating the json for each file
            website_visit['pageload_start_ts'] = time.time() # start time

            try: 
                driver.set_page_load_timeout(120)
                driver.get(url)
                website_visit['pageload_end_ts']=time.time()
                time.sleep(10)
                website_visit['post_pageload_url'] = driver.current_url   #loaded the url
                website_visit['domain'] = get_fld(url)  # the domain of every website
                website_visit['crawl_mode']= 'mobile' if isMobile == True else 'desktop'  # need to be changed later to desktop or mobile
                contents = driver.find_elements(by=By.CSS_SELECTOR,value="a, button, div, span, form, p")

                candidate = None
                screen_shot_name = get_screenshot_name(website_visit['domain'],'_pre_consent') 
                driver.save_screenshot(screen_shot_name) # taking the secreenshot before accepting

                for c in contents:
                    try: 
                        if c.text.lower().strip(" ✓›!\n") in accept_words_list:
                            candidate = c  
                            break
                    except Exception as content_e:
                        print('&&&&&&&&&&&&&&& Error in fetching content &&&&&&&&&&&&&')
                        print(str(content_e))
                        website_visit['consent_status']="errored"
                        errored_clicks_count = errored_clicks_count + 1 

                # Click the candidate
                if candidate is not None:
                    try: 
                        candidate.click()
                        website_visit['consent_status']="clicked"
                        logger.log("Successfully clicked accept for: " + url)
                        successful_clicks_count = successful_clicks_count + 1
                    except Exception as e:
                        logger.log(e)
                        website_visit['consent_status']="errored"
                        logger.log("Error in clicking accept for: " + url)
                        error_count = logger.click_error_dict['mobile' if isMobile == True else 'desktop']
                        error_count = error_count + 1
                        logger.click_error_dict['mobile' if isMobile == True else 'desktop'] = error_count
                        errored_clicks_count = errored_clicks_count + 1
                else:
                    website_visit["consent_status"]="not_found"
                    logger.log("Accept button not found for: " + url)
                    not_found_clicks.append(url)

                time.sleep(10)
                screen_shot_name_post = get_screenshot_name(website_visit['domain'],'_post_consent')
                driver.save_screenshot(screen_shot_name_post) # taking the secreenshot after  accepting the cookies
                req_response=list()

                for request in driver.requests:
                    req_resp={}
                    req_resp['request_url']=request.url
                    if (request.response is not None):
                        req_resp['timestamp']=request.response.headers['date']
                    req_headers={}
                    for header in request.headers:
                        if(header.lower()=='cookie'):
                            req_headers[header]=request.headers[header]
                        else:
                            req_headers[header]=request.headers[header][0:512]
                        
                    req_resp['request_headers']=req_headers
                    if (request.response is not None):
                        resp_headers={}
                        for response in request.response.headers:
                            resp_headers[response]=request.response.headers[response][0:512]
                        req_resp['response_headers']=resp_headers
                        req_response.append(req_resp)
                website_visit['requests']=req_response
                file_name=website_visit['domain'] +'_'+ parsed_stuff.isMobile+ '.json'

                with open(file_name, 'w') as out:
                    json.dump(website_visit, out,indent=4)
            
            except TimeoutException as time_out_exc:#, WebDriverException, Exception as e:
                logger.log('Timeout exception: '+ str(time_out_exc.msg) + ' ' + url)
                error_count = logger.time_out_error_dict['mobile' if isMobile == True else 'desktop']
                error_count = error_count + 1
                logger.time_out_error_dict['mobile' if isMobile == True else 'desktop'] = error_count 
                driver.quit()
            except WebDriverException as web_driver_exc:
                logger.log('Webdriver exception: '+ str(web_driver_exc.msg) + ' ' + url) 
                driver.quit()   
            except Exception as exc:
                logger.log('Other exception: '+ str(exc.msg) + ' ' + url)  
                driver.quit()
        #print('$$$$$$$$$ Trying to quit driver after computation $$$$$$$$$$$$$$')
        try:
            driver.quit()  
        except(WebDriverException,Exception) as general_exc:
            logger.log('Quitting driver when already quit '+ str(general_exc))
    logger.dump_json()
    logger.dump_counter_logs()

if __name__ == "__main__":
    main()

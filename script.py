# -*- coding: utf-8 -*-
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from tld import get_fld
import time
import json
import argparse
import csv
from UniversalLogger import UniversalLogger
from error_handler import ErrorHandler
import base64

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
                        if url_data_str.startswith("www."):
                            url_data_str = "http://" + url_data_str
                        else:
                            url_data_str = "http://www." + url_data_str
                    urls.append(url_data_str)
        urls.remove('http://www.domain')

    build_url()

    def execute_cdp(driver):
        SCR = """
        // overwrite a given function
        const interceptFunctionCall = function (elementType, funcName) {
            // save the original function using a closure
            const origFunc = elementType.prototype[funcName];
            // overwrite the object property
            Object.defineProperty(elementType.prototype, funcName, {
                "value": function () {
                    // execute the original function
                    const retVal = origFunc.apply(this, arguments);
                    // initialize call details with return value and arguments
                    callDetails = {
                        elementType: elementType.name,
                        funcName: funcName,
                        args: arguments,
                        retVal: retVal
                        };
                    const LS_CANVAS_KEY_NAME = "__canvas_intercepted_calls__";
                    // read the existing calls from local storage
                    let recordedCalls = JSON.parse(localStorage.getItem(LS_CANVAS_KEY_NAME));
                    if(recordedCalls == null){
                        recordedCalls = []; // initialize
                    }
                    // add the current call to the list
                    recordedCalls.push(callDetails);
                    // save the updated list to local storage
                    localStorage.setItem(LS_CANVAS_KEY_NAME, JSON.stringify(recordedCalls));
                    console.log('[CANVAS]', elementType.name, funcName, arguments, retVal);
                    return retVal;
                }
            });
        };
        // you may need to intercept more functions
        interceptFunctionCall(HTMLCanvasElement, 'toDataURL');
        interceptFunctionCall(CanvasRenderingContext2D, 'fillText');
        """
        driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {'source': SCR}
        )

    def perform_canvas_fp(driver,url):
        img_ret_value = (driver.execute_script("return localStorage.getItem('__canvas_intercepted_calls__')"))
        if img_ret_value != None:
            img = img_ret_value.split("base64,")
            img_base64 = str.encode(img[1])
            if isMobile == True:
                prefix_fp = 'mobile_'
            else:
                prefix_fp = 'desktop_'
            img_name = 'canvas_fp_' + prefix_fp + str(get_fld(url))+'.png'
            with open(img_name, "wb") as fh:
                fh.write(base64.decodebytes(img_base64))
                logger.log('Generated canvas_fp image for: '+ url)
        else:
            logger.log('Unable to get canvas_fp for url: '+ url)


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
        nodelist = []
        nodes = driver.find_elements(by=By.CSS_SELECTOR,value="a, button, div, span, form, p") 
        for node in nodes:
            print(node)
            ActionChains(driver).move_to_element(node).click().perform()
            time.sleep(0.5)
            nodelist.append(driver.find_elements(by=By.CSS_SELECTOR,value="a, button, div, span, form, p").text)
            ActionChains(driver).move_to_element(node).click().perform()

        driver.execute_script("arguments[0].click();",element)

    stripped_urls_2 = urls[0:10]#['http://www.aliyun.com','http://www.msedge.net','http://www.adnxs.com','http://www.amsterdam.craigslist.org','http://www.alicdn.com']
    stripped_urls = ['http://www.youtube.com','http://www.baidu.com']
    
    for url in stripped_urls: 
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
                execute_cdp(driver)
                driver.get(url)
                website_visit['pageload_end_ts']=time.time()
                time.sleep(10)
                website_visit['post_pageload_url'] = driver.current_url   #loaded the url
                website_visit['domain'] = get_fld(url)  # the domain of every website
                website_visit['crawl_mode']= 'mobile' if isMobile == True else 'desktop'  # need to be changed later to desktop or mobile
                contents = driver.find_elements(by=By.CSS_SELECTOR,value="a, button, div, span, form, p")
                perform_canvas_fp(driver,url)
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
                       # try_clicking_button_with_script(driver)
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
            
            except TimeoutException as time_out_exc:
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
        try:
            driver.quit()  
        except(WebDriverException,Exception) as general_exc:
            logger.log('Quitting driver when already quit '+ str(general_exc))
    logger.dump_json()
    logger.dump_counter_logs()

if __name__ == "__main__":
    main()

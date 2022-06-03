from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
import requests
import requests.exceptions
from UniversalLogger import UniversalLogger
from selenium.common.exceptions import WebDriverException

class ErrorHandler:
    ## Instance variables
    url_to_be_tested: str
    driver: webdriver
    logger : UniversalLogger

    ## Local variables
    error_counter = 0 
    tls_error_count = 0 
    time_out_error_count = 0 
    domain_error_count = 0
    isMobile = False 

    def __init__(self, driver, url_to_be_tested, logger,isMobile):
        print('^^^^^ Error handler init ^^^^^^')
        self.driver = driver
        self.url_to_be_tested = url_to_be_tested 
        self.logger = logger
        self.isMobile = isMobile
        print(url_to_be_tested)    
        self.run_all_checks()
        
    def check_TLS(self):                                         # TLS error
        try:
            print('^^^^^ checking for TLS ^^^^^^^^')
            requests.get(self.url_to_be_tested, timeout=60)
        except requests.exceptions.Timeout as e:
            self.error_counter = self.error_counter + 1
            self.logger.log('TLS_error_timeout: '+ self.url_to_be_tested)
        except requests.exceptions.RequestException as e:
            if 'CERTIFICATE_VERIFY_FAILED' in str(e):
                self.logger.log('TLS_error: '+ self.url_to_be_tested)
            elif 'hostname' in str(e):
                self.logger.log('TLS_error: '+ self.url_to_be_tested)
            error_count = self.logger.tls_error_dict['mobile' if self.isMobile == True else 'desktop']
            error_count = error_count + 1
            self.logger.tls_error_dict['mobile' if self.isMobile == True else 'desktop'] = error_count 
            self.error_counter = self.error_counter + 1

    

    def time_out(self):                              # timeout error code 
        try:
            self.driver.set_page_load_timeout(60)
            if self.url_to_be_tested != None:
                self.driver.get(self.url_to_be_tested)
        except (TimeoutException,WebDriverException) as e:
            self.logger.log('time_out: '+str(e.msg) + ' ' + self.url_to_be_tested)
            self.error_counter = self.error_counter + 1 
            

    def domain_not_exit(self):      # domian does not exit we do not need this in anaylsis report
        try:
            print('^^^^^^ trying to seaarch for domain ^^^^^^^^')
            requests.get(self.url_to_be_tested,timeout=60)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            self.error_counter = self.error_counter + 1
            self.logger.log('domain_does_not_exit: '+ str(e) +' '+ self.url_to_be_tested)


    def run_all_checks(self):
        try:
            print('^^^^ Started running all checks ^^^^^')
            self.check_TLS()
            #self.time_out()
            self.domain_not_exit()
        except (Exception, WebDriverException, TimeoutException, ConnectionAbortedError, ConnectionError,ConnectionRefusedError,ConnectionResetError) as e:
            self.logger.log('Unknown exception: '+ str(e) +' '+ self.url_to_be_tested) 
            self.error_counter = self.error_counter + 1
            #self.driver.refresh()


            

   
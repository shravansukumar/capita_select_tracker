from inspect import ismodule
from xmlrpc.client import boolean
from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
import requests
from UniversalLogger import UniversalLogger

class ErrorHandler:
    ## Instance variables
    url_to_be_tested: str
    driver: webdriver
    logger : UniversalLogger
    isMobile: bool 

    ## Local variables
    error_counter_mobile = 0 
    error_counter_desktop=0
    tls_error_count_mobile = 0 
    time_out_error_count_mobile = 0 
    domain_error_count_mobile = 0 
    tls_error_count_desktop = 0 
    time_out_error_count_desktop = 0 
    domain_error_count_desktop = 0 


    def __init__(self, driver, url_to_be_tested,logger,isMobile):
        self.driver = driver
        self.url_to_be_tested = url_to_be_tested 
        self.logger = logger
        self.isMobile=isMobile
        print(url_to_be_tested)    
        self.run_all_checks()
        
    def check_TLS(self):                                         # TLS error
        try:
            requests.get(self.url_to_be_tested)
        except requests.exceptions.RequestException as e:
            if 'CERTIFICATE_VERIFY_FAILED' in str(e):
                self.logger.log('TLS_error: '+ self.url_to_be_tested)
            elif 'hostname' in str(e):
                self.logger.log('TLS_error: '+ self.url_to_be_tested)
            if (self.isMobile):
                self.error_counter_mobile = self.error_counter_mobile + 1
                self.tls_error_count_mobile=self.tls_error_count_mobile+1
            else:
                self.error_counter_desktop= self.error_counter_desktop + 1
                self.tls_error_count_desktop=self.tls_error_count_desktop+1
            

    def time_out(self):                              # timeout error code 
        try:
            self.driver.set_page_load_timeout(30)
            self.driver.get(self.url_to_be_tested)
        except TimeoutException as e:
            self.logger.log('time_out: '+ self.url_to_be_tested)
            if (self.isMobile):
                self.error_counter_mobile = self.error_counter_mobile + 1 
                self.time_out_error_count_mobile=self.time_out_error_count_mobile+1
            else:
                self.error_counter_desktop= self.error_counter_desktop + 1 
                self.time_out_error_count_desktop=self.time_out_error_count_desktop+1
            

    def domain_not_exit(self):      # domian does not exit we do not need this in anaylsis report
        try:
            requests.get(self.url_to_be_tested)
        except requests.exceptions.ConnectionError as e:
            self.logger.log('domain_does_not_exist: '+ self.url_to_be_tested)
            if (self.isMobile):
                self.error_counter_mobile = self.error_counter_mobile + 1
                self.domain_error_count_mobile=self.domain_error_count_mobile+1


    def run_all_checks(self):
        try:
            self.check_TLS()
            self.time_out()
            self.domain_not_exit()
        except Exception as e:
            self.logger.log('Unknown exception: '+ str(e) +' '+ self.url_to_be_tested) 
            if (self.isMobile):
                self.error_counter_mobile = self.error_counter_mobile + 1
            else:
                self.error_counter_desktop=self.error_counter_desktop + 1



            

   
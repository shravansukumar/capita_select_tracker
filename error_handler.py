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


driver = webdriver.Firefox() 

try: 
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

except Exception as e:
    print("Other Execption "+ str(e))
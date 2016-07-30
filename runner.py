#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

"""Quick test runner

Edit the source at indicated spots to pick what gets run and
where. After a run, you are dropped to IPython debugger.
Press
  q to terminate the runner
  c to reload test sources and do new run in same browser window

Keep this configured for the local Chrome on jdanek's laptop.

If there are ever multiple users, I may switch to CLI parameters,
env variables, or something like that.
"""

import importlib
import time
import traceback

from selenium import webdriver
from IPython.core.debugger import Tracer

import webdriver.page_objects as page_objects
import webdriver.test_connect_page as test_connect_page
import webdriver.test_overview_page as test_overview_page

# useful inside the IPython debugger
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# BASE_URL = 'http://10.0.2.2:8080/hawtio'
# CONSOLE_IP = '10.0.2.2'

BASE_URL = 'http://127.0.0.1:8080/hawtio'
CONSOLE_IP = '127.0.0.1'


def initialize_local_chrome():
    options = webdriver.ChromeOptions()
    options.binary_location = '/home/jdanek/.nix-profile/bin/google-chrome-stable'
    driver = webdriver.Chrome(chrome_options=options)
    return driver


def initialize_remote_selenium():

    selenium_url = 'http://192.168.33.10:4444/wd/hub'
    capabilities = {'browserName': 'chrome'}

    # selenium_url = 'http://127.0.0.1:4444/wd/hub'
    # capabilities = {
    #     'browserName': 'jbrowserdriver',
    #     'version': '1',
    #     'platform': 'ANY',
    # }

    driver = webdriver.Remote(selenium_url, desired_capabilities=capabilities)
    driver.implicitly_wait(10)
    return driver


def deinitialize_selenium(driver: webdriver.Remote):
    driver.close()


def reload_test(selenium):
    """Reloads modules and instantiates a test.

    Edit this method to choose which test you want to be executed
    """
    base_url = BASE_URL
    console_ip = CONSOLE_IP

    importlib.reload(page_objects)
    importlib.reload(test_connect_page)
    importlib.reload(test_overview_page)

    suite = test_connect_page.TestConnectPage().setup(base_url, console_ip, selenium)
    test = suite.test_submit_form_with_enter_key
    return test


def main():

    selenium = initialize_local_chrome()
    # selenium = initialize_remote_selenium()
    try:
        while True:
            thence = time.time()
            print('Beginning a new run')
            test = reload_test(selenium)

            try:
                test()
            except:
                traceback.print_exc()

            print('Run finished. Took {}. Continue?'.format(time.time() - thence))
            Tracer(colors='NoColor')()

    finally:
        deinitialize_selenium(selenium)


# Tip: select everything from here up and Execute Selection in Console (Alt+Shift+E in Intellij)
if __name__ == '__main__':
    main()

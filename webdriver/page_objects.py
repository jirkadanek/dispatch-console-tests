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

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ConnectPage(object):
    def __init__(self, selenium: webdriver.Remote):
        self.selenium = selenium
        self.wait_for_frameworks()

        self.host = self.selenium.find_element(By.NAME, 'address')

        # without waiting, got TypeError - undefined is not a function (evaluating '_getTagName(currWindow).toLowerCase()')
        self.port = self.selenium.find_element(By.NAME, 'port')

        self.connect_button = self.selenium.find_element(By.CSS_SELECTOR, '#dispatch-login-container button')

    @classmethod
    def open(cls, base_url, selenium):
        url = base_url + '/dispatch_plugin'
        selenium.get(url)
        return ConnectPage(selenium)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Connect link in the top bar to be active
        locator = (By.CSS_SELECTOR, '.active a[ng-href="#/dispatch_plugin/connect"]')
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))

    def find_wait_clickable(self, by, value, root=None):
        locator = (by, value)
        element = WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(locator))
        return element

    def wait_for_frameworks(self):
        """Checks whether the UI frameworks are changing the UI

        Spies on jQuery and Angular, exactly what is needed.

        http://stackoverflow.com/questions/25062969/testing-angularjs-with-selenium
        """
        script = """
try {
  if (document.readyState !== 'complete') {
    return false; // Page not loaded yet
  }
  if (window.jQuery) {
    if (window.jQuery.active) {
      return false;
    } else if (window.jQuery.ajax && window.jQuery.ajax.active) {
      return false;
    }
  }
  if (window.angular) {
    if (!window.qa) {
      // Used to track the render cycle finish after loading is complete
      window.qa = {
        doneRendering: false
      };
    }
    // Get the angular injector for this app (change element if necessary)
    var injector = window.angular.element('body').injector();
    // Store providers to use for these checks
    var $rootScope = injector.get('$rootScope');
    var $http = injector.get('$http');
    var $timeout = injector.get('$timeout');
    // Check if digest
    if ($rootScope.$$phase === '$apply' || $rootScope.$$phase === '$digest' || $http.pendingRequests.length !== 0) {
      window.qa.doneRendering = false;
      return false; // Angular digesting or loading data
    }
    if (!window.qa.doneRendering) {
      // Set timeout to mark angular rendering as finished
      $timeout(function() {
        window.qa.doneRendering = true;
      }, 0);
      return false;
    }
  }
  return true;
} catch (ex) {
  return false;
}
"""
        self.wait_for(lambda: self.selenium.execute_script(script))

    def wait_for(self, condition):
        limit = 10
        t = 0
        d = 0.3
        while True:
            result = condition()
            if result:
                # print('waited for', t)
                return
            if t > limit:
                assert t < limit
            time.sleep(d)
            t += d

    def initialize(self):
        self.host = self.selenium.find_element(By.ID, '')
        self.port = self.selenium.find_element(By.ID, '')
        self.connect_button = self.selenium.find_element(By.ID, '')

    def connect_to(self, host=None, port=None):
        self.host.clear()
        self.port.clear()
        if host is not None:
            self.host.send_keys(host)
        if port is not None:
            self.port.send_keys(port)


class OverviewPage(object):
    def __init__(self, selenium: webdriver.Remote):
        self.selenium = selenium

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Overview link in the top bar to be active
        locator = (By.CSS_SELECTOR, '.active a[ng-href="#/dispatch_plugin/overview"]')
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))

    @property
    def entities_tab(self) -> WebElement:
        locator = (By.CSS_SELECTOR, 'a[ng-href="#/dispatch_plugin/list"]')
        return WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located(locator))

    @property
    def overview_tab(self) -> WebElement:
        locator = (By.CSS_SELECTOR, 'a[ng-href="#/dispatch_plugin/overview"]')
        return WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located(locator))
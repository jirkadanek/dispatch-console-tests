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

from abc import ABCMeta, abstractmethod
import time
from unittest.mock import Mock

import pytest
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from typing import Type, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


PLUGIN_NAME = 'dispatch_hawtio_console'


class PageObject(object):
    def __init__(self, selenium: webdriver.Remote):
        self.selenium = selenium

    def wait_locate_visible_element(self, locator) -> WebElement:
        timeout = 10
        return WebDriverWait(self.selenium, timeout).until(EC.presence_of_element_located(locator))

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
        self.wait_for_angular()

    @staticmethod
    def wait_for(condition):
        timeout = 10
        t = 0
        d = 0.3
        while True:
            result = condition()
            if result:
                # print('waited for', t)
                return
            if t > timeout:
                assert t < timeout
            time.sleep(d)
            t += d

    def wait_for_angular(self, element: str = "html"):
        # waitForAngular()
        # https://github.com/angular/protractor/blob/71532f055c720b533fbf9dab2b3100b657966da6/lib/clientsidescripts.js#L51
        self.selenium.set_script_timeout(10)
        self.selenium.execute_async_script("""
        callback = arguments[arguments.length - 1];
        angular.element('{}').injector().get('$browser').notifyWhenNoOutstandingRequests(callback);""".format(element))


class LogsPage(PageObject):
    @classmethod
    def open(cls, base_url, selenium):
        url = '{}/logs'.format(base_url)
        selenium.get(url)
        return cls(selenium)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        locator = (By.CSS_SELECTOR, '.active a[ng-href="#/logs"]')
        WebDriverWait(selenium, 30).until(EC.visibility_of_element_located(locator))


class ConnectPage(PageObject):
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)
        self.wait_for_frameworks()

        # ensure that all these things are in the page
        _ = self.host
        _ = self.port
        _ = self.connect_button

    @property
    def host(self):
        return self.wait_locate_visible_element((By.NAME, 'address'))

    @property
    def port(self):
        return self.wait_locate_visible_element((By.NAME, 'port'))

    @property
    def connect_button(self):
        return self.selenium.find_element(By.CSS_SELECTOR, '#dispatch-login-container button')

    @classmethod
    def url(cls, base_url):
        return base_url + '/{}'.format(PLUGIN_NAME)

    @classmethod
    def open(cls, base_url, selenium):
        selenium.get(cls.url(base_url))
        return cls(selenium)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Connect link in the top bar to be active
        locator = (By.CSS_SELECTOR, '.active a[ng-href="#/{}/connect"]'.format(PLUGIN_NAME))
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))

    def find_wait_clickable(self, by, value, root=None):
        locator = (by, value)
        element = WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(locator))
        return element

    def connect_to(self, host=None, port=None):
        self.host.clear()
        self.wait_for_frameworks()
        if host is not None:
            self.host.send_keys(host)
            self.wait_for_frameworks()
        self.port.clear()
        if port is not None:
            self.port.send_keys(port)


class PluginPage(PageObject):
    """PluginPage is page inside dispatch-hawtio-plugin. It has a treeview on the left."""
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)
        self.node_count = None  # type: int

    @property
    def entities_tab(self) -> WebElement:
        locator = (By.CSS_SELECTOR, 'a[ng-href="#/{}/list"]'.format(PLUGIN_NAME))
        return self.wait_locate_visible_element(locator)

    @property
    def overview_tab(self) -> WebElement:
        locator = (By.CSS_SELECTOR, 'a[ng-href="#/{}/overview"]'.format(PLUGIN_NAME))
        return self.wait_locate_visible_element(locator)

    @property
    def expander_locator(self):
        return By.CSS_SELECTOR, '.dynatree-node > .dynatree-expander'

    def expand_tree(self, node_count):
        """expand_tree expands treeview (dynatree) by clicking expander arrows one by one"""
        self.wait_for_frameworks()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(self.expander_locator))
        WebDriverWait(self.selenium, 10).until(lambda _: len(self.expanders) == node_count)

        # least-work way to fight ElementNotVisibleException: Message: Cannot click on element, and
        # http://stackoverflow.com/questions/37781539/selenium-stale-element-reference-element-is-not-attached-to-the-page-document/38683022
        def loop():
            self.wait_for_frameworks()
            for expander in self.expanders:  # type: WebElement
                node = self.retry_on_exception(NoSuchElementException, lambda: expander.find_element(By.XPATH, './..'))
                if self.is_expanded(node):
                    continue
                WebDriverWait(self.selenium, 10).until(lambda _: expander.is_displayed())
                self.wait_for_frameworks()
                expander.click()
                self.wait_for_frameworks()
        self.retry_on_exception(StaleElementReferenceException, loop)

        self.assert_tree_expanded()

    def assert_tree_expanded(self):
        def loop():
            self.wait_for_frameworks()
            assert all(self.is_expanded(e.find_element(By.XPATH, './..')) for e in self.expanders)
        self.retry_on_exception(StaleElementReferenceException, loop)

    def is_expanded(self, node: WebElement):
        return 'dynatree-expanded' in node.get_attribute('class')

    @property
    def expanders(self) -> List[WebElement]:
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node > .dynatree-expander')

    @property
    def expanded_nodes(self) -> List[WebElement]:
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node.dynatree-expanded')

    def retry_on_exception(self, exception, test_function, retries=50):
        for _ in range(retries):
            try:
                return test_function()
            except exception as e:
                pass
        pytest.fail("Kept getting Exception")


class StandalonePluginPage(PageObject):
    @property
    def entities_tab(self) -> WebElement:
        locator = (By.CSS_SELECTOR, 'li > a[ng-href="#!/list"]')
        return self.wait_locate_visible_element(locator)

    @property
    def overview_tab(self) -> WebElement:
        locator = (By.CSS_SELECTOR, 'li > a[ng-href="#!/overview"]')
        return self.wait_locate_visible_element(locator)

    def wait_for_angular(self, element: str = "body"):
        return super().wait_for_angular(element)

    @property
    def expander_locator(self):
        return By.CSS_SELECTOR, '.dynatree-node > .fa-angle'

    @property
    def expanders(self) -> List[WebElement]:
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node > .fa-angle')


class OverviewPage(PluginPage):
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)
        self.node_count = 5
        # Wait for at least one node expander to appear
        _ = self.wait_locate_visible_element(self.expander_locator)

    @classmethod
    def url(cls, base_url):
        return '{}/{}/overview'.format(base_url, PLUGIN_NAME)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Overview link in the top bar to be active
        locator = (By.CSS_SELECTOR, '.active a[ng-href="#/{}/overview"]'.format(PLUGIN_NAME))
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))


class EntitiesPage(PluginPage):
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)
        self.node_count = 17
        # Wait for at least one node expander to appear
        _ = self.wait_locate_visible_element(self.expander_locator)

    @classmethod
    def url(cls, base_url):
        return '{}/{}/links'.format(base_url, PLUGIN_NAME)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Entities link in the top bar to be active
        locator = (By.CSS_SELECTOR, '.active a[ng-href="#/{}/list"]'.format(PLUGIN_NAME))
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))


# TODO: the order of predecessors matters here; the class hierarchy probably needs changing
class StandaloneOverviewPage(StandalonePluginPage, OverviewPage):
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)
        # Wait for at least one node expander to appear
        _ = self.wait_locate_visible_element(self.expander_locator)

    @classmethod
    def url(cls, base_url: str) -> str:
        return '{}/#!/overview'.format(base_url)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Overview link in the top bar to be active
        locator = (By.CSS_SELECTOR, 'li.active > a[ng-href="#!/overview"]')
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))


class StandaloneEntitiesPage(StandalonePluginPage, EntitiesPage):
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)
        # Wait for at least one node expander to appear
        _ = self.wait_locate_visible_element(self.expander_locator)

    @classmethod
    def url(cls, base_url: str) -> str:
        return '{}/#!/list'.format(base_url)

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Overview link in the top bar to be active
        locator = (By.CSS_SELECTOR, 'li.active > a[ng-href="#!/list"]')
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))


class StandaloneConnectPage(ConnectPage):
    def __init__(self, selenium: webdriver.Remote):
        super().__init__(selenium)

    @classmethod
    def url(cls, base_url: str) -> str:
        return base_url

    @classmethod
    def wait(cls, selenium: webdriver.Remote):
        # wait for Connect link in the top bar to be active
        locator = (By.CSS_SELECTOR, 'a[ng-href="#!/connect"]')
        WebDriverWait(selenium, 30).until(EC.presence_of_element_located(locator))

    # TODO: again this is bad class hierarchy
    def wait_for_angular(self, element: str = "body"):
        return super().wait_for_angular(element)


class PageObjectContainer(object, metaclass=ABCMeta):
    @property
    @abstractmethod
    def overview_page(self) -> Type[OverviewPage]:
        pass

    @property
    @abstractmethod
    def entities_page(self) -> Type[EntitiesPage]:
        pass

    @property
    @abstractmethod
    def connect_page(self) -> Type[ConnectPage]:
        pass

    @property
    @abstractmethod
    def logs_page(self) -> Type[LogsPage]:
        pass


class HawtioPageObjectContainer(PageObjectContainer):
    @property
    def overview_page(self):
        return OverviewPage

    @property
    def entities_page(self):
        return EntitiesPage

    @property
    def connect_page(self):
        return ConnectPage

    @property
    def logs_page(self):
        return LogsPage


class StandalonePageObjectContainer(PageObjectContainer):
    @property
    def overview_page(self):
        return StandaloneOverviewPage

    @property
    def entities_page(self):
        return StandaloneEntitiesPage

    @property
    def connect_page(self):
        return StandaloneConnectPage

    @property
    def logs_page(self):
        return Mock(side_effect=lambda: pytest.skip("Test attempted to use NonexistentPage, so it is skipped."))

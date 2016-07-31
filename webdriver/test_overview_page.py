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

from typing import List

import pytest
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver.page_objects import PageObjectContainer
from .page_objects import ConnectPage, OverviewPage
from .test_connect_page import TestCase


class TestOverviewPage(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, base_url: str, console_ip: str, pages: PageObjectContainer, selenium: webdriver.Remote):
        self.base_url = base_url
        self.console_ip = console_ip
        self.console_port = 5673
        self.ConnectPage = pages.connect_page
        self.OverviewPage = pages.overview_page
        self.selenium = selenium
        self.test_name = None
        return self

    @pytest.mark.nondestructive
    def test_open_overview_page(self):
        page = self.given_overview_page()

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-434')
    def test_expanding_tree(self):
        # currently broken, uncomenting eventually crashes ie driver
        # least-work way to fight ElementNotVisibleException: Message: Cannot click on element
        # self.selenium.implicitly_wait(10)

        self.test_name = 'test_expanding_tree'
        node_count = 4
        page = self.given_overview_page()

        expander_locator = (By.CSS_SELECTOR, '.dynatree-node > .dynatree-expander')
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(expander_locator))
        WebDriverWait(self.selenium, 10).until(lambda _: len(self.expanders) == node_count)

        def f():
            page.wait_for_frameworks()
            for expander in self.expanders:  # type: WebElement
                node = self.fight_exception(NoSuchElementException, lambda: expander.find_element(By.XPATH, './..'))
                if self.is_expanded(node):
                    continue
                WebDriverWait(self.selenium, 10).until(lambda _: expander.is_displayed())
                page.wait_for_frameworks()
                expander.click()
                page.wait_for_frameworks()
        self.fight_exception(StaleElementReferenceException, f)

        # all dynatree nodes should be expanded
        def g():
            page.wait_for_frameworks()
            assert all(self.is_expanded(e.find_element(By.XPATH, './..')) for e in self.expanders)
        self.fight_exception(StaleElementReferenceException, g)
        self.take_screenshot("10")
        self.when_navigate_to_entities_page_and_back(page)

        assert len(self.expanded_nodes) == node_count
        self.take_screenshot("20")

    def is_expanded(self, node: WebElement):
        return 'dynatree-expanded' in node.get_attribute('class')

    def given_overview_page(self):
        connect = self.ConnectPage.open(self.base_url, self.selenium)
        connect.wait_for_frameworks()
        self.ConnectPage.wait(self.selenium)
        connect.wait_for_frameworks()

        connect.connect_to(self.console_ip, self.console_port)
        connect.connect_button.click()
        self.OverviewPage.wait(self.selenium)
        overview = self.OverviewPage(self.selenium)
        overview.wait_for_frameworks()
        return overview

    def when_navigate_to_entities_page_and_back(self, page):
        page.entities_tab.click()
        page.wait_for_frameworks()
        page.overview_tab.click()
        OverviewPage.wait(self.selenium)
        page.wait_for_frameworks()

    @property
    def expanders(self) -> List[WebElement]:
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node > .dynatree-expander')

    @property
    def expanded_nodes(self) -> List[WebElement]:
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node.dynatree-expanded')

    def fight_exception(self, exception, test_function):
        for _ in range(50):
            try:
                return test_function()
            except exception as e:
                pass
        pytest.fail("Kept getting Exception")

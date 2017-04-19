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

import os.path
import pytest
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .page_objects import ConnectPage, OverviewPage
from .test_connect_page import TestCase


class TestOverviewPage(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, base_url: str, console_ip: str, selenium: webdriver.Remote):
        self.base_url = base_url
        self.console_ip = console_ip
        self.selenium = selenium
        self.test_name = None
        return self

    @pytest.mark.nondestructive
    def test_open_overview_page(self):
        page = self.given_overview_page()

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-434')
    def test_expanding_tree(self):
        self.test_name = 'test_expanding_tree'
        node_count = 4
        page = self.given_overview_page()
        expanders = self.expanders
        assert len(expanders) == node_count

        for expander in expanders:
            node = expander.find_element(By.XPATH, './..')
            if self.is_expanded(node):
                continue
            expander.click()

        page.wait_for_frameworks()
        # all dynatree nodes should be expanded
        assert all(self.is_expanded(e.find_element(By.XPATH, './..')) for e in self.expanders)
        self.take_screenshot("10")
        self.when_navigate_to_entities_page_and_back(page)

        assert len(self.expanded_nodes) == node_count
        self.take_screenshot("20")

    def is_expanded(self, node: WebElement):
        return 'dynatree-expanded' in node.get_attribute('class')

    def given_overview_page(self):
        connect = ConnectPage.open(self.base_url, self.selenium)
        connect.wait_for_frameworks()
        ConnectPage.wait(self.selenium)
        connect.wait_for_frameworks()

        connect.connect_to(self.console_ip)
        connect.connect_button.click()
        OverviewPage.wait(self.selenium)
        overview = OverviewPage(self.selenium)
        overview.wait_for_frameworks()
        return overview

    def when_navigate_to_entities_page_and_back(self, page):
        page.entities_tab.click()
        page.wait_for_frameworks()
        page.overview_tab.click()
        OverviewPage.wait(self.selenium)
        page.wait_for_frameworks()

    @property
    def expanders(self):
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node > .dynatree-expander')

    @property
    def expanded_nodes(self):
        return self.selenium.find_elements(By.CSS_SELECTOR, '.dynatree-node.dynatree-expanded')
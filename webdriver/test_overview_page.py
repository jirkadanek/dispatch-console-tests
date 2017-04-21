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
from selenium import webdriver

from webdriver.page_objects import PageObjectContainer
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
        self.test_name = 'test_expanding_tree'
        page = self.given_overview_page()

        page.expand_tree(page.node_count)
        self.take_screenshot("10")

        self.when_navigate_to_entities_page_and_back(page)
        assert len(page.expanded_nodes) == page.node_count
        self.take_screenshot("20")

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
        self.OverviewPage.wait(self.selenium)
        page.wait_for_frameworks()

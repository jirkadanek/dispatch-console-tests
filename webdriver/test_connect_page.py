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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .page_objects import ConnectPage, OverviewPage


class TestCase(object):
    """
    Subclasses have to declare the following fields:
        self.test_name
        self.selenium
    """
    def take_screenshot(self, name):
        """Saves a screenshot into the current directory"""
        if not self.test_name:
            raise RuntimeError('self.test_name is not set')
        filename = '{}__{}.png'.format(self.test_name, name)
        self.selenium.get_screenshot_as_file(os.path.abspath(filename))


class TestConnectPage(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, base_url: str, console_ip: str, selenium: webdriver.Remote):
        self.base_url = base_url
        self.console_ip = console_ip
        self.selenium = selenium
        self.test_name = None
        return self

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-433')
    def test_redirect_to_connect_page(self):
        bookmark = '{}/overview'.format(self.base_url)

        self.selenium.get(bookmark)
        ConnectPage.wait(self.selenium)
        page = ConnectPage(self.selenium)  # check it is not just empty page with toolbar
        self.then_no_js_error()

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-416')
    def test_wrong_ip(self):
        self.test_name = 'test_wrong_ip'
        page = self.given_connect_page()
        page.connect_to('111222', None)

        page.connect_button.click()
        page.wait_for_frameworks()

        self.then_error_message_says('There was a connection error: Connection failed')
        self.take_screenshot('20')

        self.then_no_js_error()

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-428')
    def test_wrong_port(self):
        self.test_name = 'test_wrong_port'

        invalid_port = '0'
        closed_port = '11265'

        page = self.given_connect_page()

        page.connect_to('127.0.0.1', invalid_port)
        page.wait_for_frameworks()
        assert not page.connect_button.is_enabled()

        page.connect_to('127.0.0.1', closed_port)
        page.connect_button.click()
        page.wait_for_frameworks()
        self.then_error_message_says("There was a connection error: Connection failed")
        self.take_screenshot('10')

        self.then_no_js_error()

    @pytest.mark.nondestructive
    @pytest.mark.parametrize("when_correct_details", [
        lambda self, page: self.when_correct_details(page),
        lambda self, page: page.connect_to(self.console_ip),
        lambda self, page: page.connect_to(),
    ])
    def test_correct_details(self, when_correct_details):
        self.test_name = 'test_correct_details'
        page = self.given_connect_page()
        when_correct_details(self, page)
        page.connect_button.click()
        self.then_login_succeeds()
        self.then_no_js_error()

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-439')
    def test_submit_form_with_enter_key(self):
        self.test_name = 'test_submit_form_with_enter_key'
        page = self.given_connect_page()
        self.when_correct_details(page)
        page.port.send_keys(Keys.ENTER)
        self.then_login_succeeds()
        self.then_no_js_error()

    def given_connect_page(self):
        page = ConnectPage.open(self.base_url, self.selenium)
        return page

    def when_correct_details(self, page):
        page.connect_to(self.console_ip, '5673')

    def then_login_succeeds(self):
        try:
            OverviewPage.wait(self.selenium)
        except TimeoutException:
            pytest.fail("login did not succeed (within time limit)")

    def then_error_message_says(self, message):
        # without any sort of waiting the test is flaky. suggests that wait_for_frameworks does not work well
        locator = (By.CSS_SELECTOR, 'p.ng-binding')
        WebDriverWait(self.selenium, 10).until(EC.text_to_be_present_in_element(locator, message))
        error = self.selenium.find_element(*locator)
        assert error.text == message
        assert error.is_displayed()

    def then_toast_error_says(self, message):
        error = self.selenium.find_element(By.CSS_SELECTOR, '.toast-error .toast-message')
        assert error.text == message
        assert error.is_displayed()

    def then_no_js_error(self):
        log = self.selenium.get_log('browser')
        for entry in log:
            message = entry['message']
            assert 'Stack trace:' not in message


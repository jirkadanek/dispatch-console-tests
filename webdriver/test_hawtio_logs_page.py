import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from webdriver.page_objects import LogsPage
from webdriver.test_connect_page import TestCase


class TestHawtioLogsPage(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, base_url: str, console_ip: str, selenium: webdriver.Remote):
        self.base_url = base_url
        self.console_ip = console_ip
        self.selenium = selenium
        self.test_name = None
        return self

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-433')
    def test_open_hawtio_logs_page(self):
        self.test_name = 'test_open_hawtio_logs_page'
        bookmark = '{}/logs'.format(self.base_url)
        self.selenium.get(bookmark)
        LogsPage.wait(self.selenium)
        self.take_screenshot("10")
        # TODO: check it is not just empty page with toolbar
        self.then_no_js_error()

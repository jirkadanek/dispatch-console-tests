import pytest
from selenium import webdriver

from webdriver.page_objects import PageObjectContainer
from webdriver.test_connect_page import TestCase


class TestHawtioLogsPage(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, base_url: str, console_ip: str, pages: PageObjectContainer, selenium: webdriver.Remote):
        self.base_url = base_url
        self.console_ip = console_ip
        self.LogsPage = pages.logs_page
        self.selenium = selenium
        self.test_name = None
        return self

    @pytest.mark.nondestructive
    @pytest.mark.verifies(issue='DISPATCH-433')
    def test_open_hawtio_logs_page(self):
        self.test_name = 'test_open_hawtio_logs_page'
        self.given_hawtio_logs_page()
        self.take_screenshot("10")
        # TODO: check it is not just empty page with toolbar
        self.then_no_js_error()

    def given_hawtio_logs_page(self):
        page = self.LogsPage.open(self.base_url, self.selenium)
        self.LogsPage.wait(self.selenium)
        return page

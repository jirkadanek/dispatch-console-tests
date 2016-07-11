import pytest
from selenium import webdriver


def pytest_addoption(parser):
    print("adding option")
    parser.addoption("--console-ip", action="store", default="127.0.0.1",
                     help="IP for connecting to the console")


@pytest.fixture
def selenium(selenium: webdriver.Remote):
    selenium.implicitly_wait(10)
    # selenium.set_window_size(1920, 1080)
    return selenium


@pytest.fixture(scope="module")
def console_ip(request):
    return request.config.getoption("--console-ip")

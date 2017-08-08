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

from typing import Any, Dict

import pytest
from _pytest.fixtures import FixtureRequest
from selenium import webdriver
from runner import initialize_local_chrome, deinitialize_selenium

from webdriver.page_objects import HawtioPageObjectContainer, StandalonePageObjectContainer


def pytest_addoption(parser):
    parser.addoption("--local-chrome", action="store_true", default=False,
                     help='use local chrome browser, shortcut for test dev')
    parser.addoption("--console-ip", action="store", default="127.0.0.1",
                     help="IP for connecting to the console")
    parser.addoption("--console", action="store", default="hawtio",
                     help="type of console, either hawtio or stand-alone")


@pytest.fixture(scope='session')
def session_capabilities(session_capabilities: Dict[str, Any]):
    if 'browserName' in session_capabilities and session_capabilities['browserName'] == 'internet explorer':
        session_capabilities['ie.ensureCleanSession'] = True
    return session_capabilities


@pytest.fixture
def selenium(request: FixtureRequest) -> webdriver.Remote:
    if request.config.getoption('--local-chrome'):
        driver = initialize_local_chrome()
        request.addfinalizer(lambda: deinitialize_selenium(driver))
        return driver

    driver = request.getfixturevalue('selenium')  # type: webdriver.Remote
    yield driver
    # https://github.com/SeleniumHQ/docker-selenium/issues/87#issuecomment-286231268
    # todo: apparently, pytest-selenium takes care of this and double call causes me an exception
    #  https://github.com/mozilla/geckodriver/issues/732
    # driver.close()


@pytest.fixture(scope="module")
def console_ip(request):
    return request.config.getoption("--console-ip")


@pytest.fixture(scope="module")
def pages(request):
    console = request.config.getoption("--console")
    if console == 'hawtio':
        return HawtioPageObjectContainer()
    elif console == 'stand-alone':
        return StandalonePageObjectContainer()
    else:
        raise RuntimeError("Unexpected --console parameter value: ", console)

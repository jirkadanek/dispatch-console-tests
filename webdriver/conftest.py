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

import pytest
from selenium import webdriver


def pytest_addoption(parser):
    parser.addoption("--console-ip", action="store", default="127.0.0.1",
                     help="IP for connecting to the console")


@pytest.fixture
def selenium(selenium: webdriver.Remote):
    return selenium


@pytest.fixture
def capabilities(capabilities):
    # HACK: when specifying capability on command line, the "true" is sent as a string. Only a guess, but I trust it.
    # string does not work, c.f. https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/8160
    capabilities['ie.ensureCleanSession'] = True
    return capabilities


@pytest.fixture(scope="module")
def console_ip(request):
    return request.config.getoption("--console-ip")

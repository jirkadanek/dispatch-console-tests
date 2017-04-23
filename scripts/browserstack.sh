#!/usr/bin/env bash

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

# run this from the repo root

set -xe

py.test -s \
 --driver BrowserStack \
 --capability browserstack.local "true" \
 --capability browserstack.localIdentifier "${BROWSERSTACK_LOCAL_IDENTIFIER}" \
 --capability browser "${BROWSER_NAME}" \
 --capability browser_version "${VERSION}" \
 --capability os "windows" \
 --capability os_version "${PLATFORM}" \
 --capability build "travis-${TRAVIS_BUILD_NUMBER}" \
 --capability project "dispatch-console" \
 --base-url http://127.0.0.1:8080/${CONSOLE} --verify-base-url --console ${CONSOLE}



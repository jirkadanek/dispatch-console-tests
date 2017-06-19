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

# This is modified Ubuntu docker file from qpid-dispatch
#
# Differences from original version:
#   * FROM value
#   * MAINTAINER value
#   * apt-get install pkg-config
#   * cleaned up packages, like ruby, emacs, ...
#   * builds hawt.io console
#
# Notes:
#   * python-pkg-resources is not in websockify dependencies but is required

FROM debian:testing
MAINTAINER "jdanek@redhat.com"

# Install all the required packages. Some in this list were picked off from
# proton's INSTALL.md (https://github.com/apache/qpid-proton/blob/master/INSTALL.md) and the
# rest are from dispatch (https://github.com/apache/qpid-dispatch/blob/master/README)
RUN apt-get update && apt-get -y install \
    cmake \
    gcc \
    checkinstall \
    git \
    libuv1-dev \
    libssl1.0-dev \
    libsasl2-dev \
    make \
    pkg-config \
    python-dev \
    sasl2-bin \
    swig \
    valgrind \
    \
    openjdk-8-jdk \
    maven \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

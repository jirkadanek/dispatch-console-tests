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

# Gets the latest stable Debian from dockerhub
FROM debian:stable
MAINTAINER "jdanek@redhat.com"

# Install all the required packages. Some in this list were picked off from
# proton's INSTALL.md (https://github.com/apache/qpid-proton/blob/master/INSTALL.md) and the
# rest are from dispatch (https://github.com/apache/qpid-dispatch/blob/master/README)
RUN apt-get update && apt-get -y install \
    cmake \
    gcc \
    checkinstall \
    git \
    libssl-dev \
    libsasl2-dev \
    make \
    pkg-config \
    python-dev \
    sasl2-bin \
    swig \
    valgrind \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a main directory and clone the qpid-proton repo from github
RUN mkdir /main && cd /main && git clone https://github.com/apache/qpid-proton.git && cd /main/qpid-proton && mkdir /main/qpid-proton/build

WORKDIR /main/qpid-proton/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DSYSINSTALL_BINDINGS=ON -DBUILD_CPP=OFF -DBUILD_JAVA=OFF -DBUILD_PERL=OFF -DSYSINSTALL_PYTHON=ON && make && checkinstall -y --pkgname qpid-proton

# Clone the qpid-dispatch git repo
RUN cd /main && git clone https://github.com/apache/qpid-dispatch.git && mkdir /main/qpid-dispatch/build

WORKDIR /main/qpid-dispatch/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr && make && checkinstall -y --pkgname qpid-dispatch

# Add site-packages to the PYTHONPATH environment variable. This is because Ubuntu does not list the site-packages folder in the sys.path
ENV PYTHONPATH=/usr/lib/python2.7/site-packages

# Uncomment the following line if you would like to run all the dispatch unit tests and system tests. 
RUN ctest -VV

# Build the hawtio console .war file
RUN apt-get update && apt-get -y install \
    openjdk-7-jdk \
    maven \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /main/qpid-dispatch/console/hawtio
RUN mvn clean install && rm -r ~/.m2

WORKDIR /main/
CMD cp -R /main/ /console && cp -R /main/ /router

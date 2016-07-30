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

# Notes:
#   * python-pkg-resources is not in websockify dependencies but is required

FROM debian:stable
MAINTAINER "jdanek@redhat.com"

# Install all the required packages. Some in this list were picked off from proton's INSTALL.md (https://github.com/apache/qpid-proton/blob/master/INSTALL.md) and the rest are from dispatch (https://github.com/apache/qpid-dispatch/blob/master/README)
# libssl-dev because of /usr/lib/x86_64-linux-gnu/libssl.so, libssl1.0.0 has libssl.so.1.0.0
# libsasl2-dev same thing
RUN apt-get update && apt-get -y install \
    cmake \
    make \
    libssl-dev \
    libsasl2-2 \
    libsasl2-dev \
    python-dev \
    python-pkg-resources \
    sasl2-bin \
    uuid \
    websockify \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY main/main/qpid-proton/build/qpid-proton_*.deb qpid-proton.deb
COPY main/main/qpid-dispatch/build/qpid-dispatch_*.deb qpid-dispatch.deb

RUN dpkg -i qpid-proton.deb qpid-dispatch.deb
#WORKDIR /main/qpid-proton/build
#RUN  make install
#WORKDIR /main/qpid-dispatch/build
#RUN make install

# Add site-packages to the PYTHONPATH environment variable. This is because Ubuntu does not list the site-packages folder in the sys.path
ENV PYTHONPATH=/usr/lib/python2.7/site-packages

# Uncomment the following line if you would like to run all the dispatch unit tests and system tests.
#RUN ctest -VV

#WORKDIR /main/
COPY console.conf ./
RUN echo "websockify 5673 0.0.0.0:20009 & qdrouterd -c console.conf" > qdrouterd.sh
CMD ["bash", "qdrouterd.sh"]

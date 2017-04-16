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

FROM debian:testing
MAINTAINER "jdanek@redhat.com"

# Install all the required packages. Some in this list were picked off from proton's INSTALL.md (https://github.com/apache/qpid-proton/blob/master/INSTALL.md) and the rest are from dispatch (https://github.com/apache/qpid-dispatch/blob/master/README)
# TODO: do I need uuid?
RUN apt-get update && apt-get -y install \
    libssl1.0.0 \
    libsasl2-2 \
    libpython2.7 \
    python-pkg-resources \
    sasl2-bin \
    websockify \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY main/main/qpid-proton/build/qpid-proton_*.deb qpid-proton.deb
COPY main/main/qpid-dispatch/build/qpid-dispatch_*.deb qpid-dispatch.deb

RUN dpkg -i qpid-proton.deb qpid-dispatch.deb

# Add site-packages to the PYTHONPATH environment variable. This is because Ubuntu does not list the site-packages folder in the sys.path
ENV PYTHONPATH=/usr/lib/python2.7/site-packages

COPY console.conf ./
RUN echo "websockify 5673 0.0.0.0:20009 & qdrouterd -c console.conf" > qdrouterd.sh
CMD ["bash", "qdrouterd.sh"]

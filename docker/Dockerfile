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
#   * builds and runs hawt.io console
#
# Notes:
#   * python-pkg-resources is not in websockify dependencies but is required

# Gets the latest stable Debian from dockerhub
FROM debian:stable
MAINTAINER "jdanek@redhat.com"

# Install all the required packages. Some in this list were picked off from proton's INSTALL.md (https://github.com/apache/qpid-proton/blob/master/INSTALL.md) and the rest are from dispatch (https://github.com/apache/qpid-dispatch/blob/master/README)
RUN apt-get update && apt-get -y install --fix-missing gcc cmake cmake-curses-gui uuid-dev libssl-dev libsasl2-2 libsasl2-dev sasl2-bin swig python-dev ruby-dev libperl-dev git make doxygen valgrind emacs openjdk-7-jdk pkg-config python-pkg-resources maven unzip websockify && rm -rf /var/lib/apt/lists/*

# Create a main directory and clone the qpid-proton repo from github
RUN mkdir /main && cd /main && git clone https://github.com/apache/qpid-proton.git && cd /main/qpid-proton && mkdir /main/qpid-proton/build

WORKDIR /main/qpid-proton/build

# make and install proton
RUN cmake .. -DSYSINSTALL_BINDINGS=ON -DCMAKE_INSTALL_PREFIX=/usr -DSYSINSTALL_PYTHON=ON && make install

# Clone the qpid-dispatch git repo
RUN cd /main && git clone https://github.com/apache/qpid-dispatch.git && mkdir /main/qpid-dispatch/build

WORKDIR /main/qpid-dispatch/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr && make install

# Add site-packages to the PYTHONPATH environment variable. This is because Ubuntu does not list the site-packages folder in the sys.path 
ENV PYTHONPATH=/usr/lib/python2.7/site-packages

# Uncomment the following line if you would like to run all the dispatch unit tests and system tests. 
RUN ctest -VV

ENV TOMCAT_VERSION 8.0.36
ENV HAWTIO_VERSION 1.4.65

# Install Apache Tomcat
WORKDIR /main
ADD http://mirror.hosting90.cz/apache/tomcat/tomcat-8/v$TOMCAT_VERSION/bin/apache-tomcat-$TOMCAT_VERSION.zip apache-tomcat-$TOMCAT_VERSION.zip
RUN unzip apache-tomcat-$TOMCAT_VERSION.zip && rm apache-tomcat-$TOMCAT_VERSION.zip

# Download prebuilt hawtio
ADD https://oss.sonatype.org/content/repositories/public/io/hawt/hawtio-default/$HAWTIO_VERSION/hawtio-default-$HAWTIO_VERSION.war /main/apache-tomcat-$TOMCAT_VERSION/webapps/hawtio.war

# Build the hawtio console .war file
WORKDIR /main/qpid-dispatch/console/hawtio
RUN mvn clean install && rm -r ~/.m2
RUN mv target/dispatch-hawtio-console-*.war /main/apache-tomcat-$TOMCAT_VERSION/webapps/dispatch-plugin.war

RUN chmod +x /main/apache-tomcat-$TOMCAT_VERSION/bin/*.sh

WORKDIR /main/
COPY console.conf ./
RUN echo "websockify 5673 0.0.0.0:20009 & bash /main/apache-tomcat-$TOMCAT_VERSION/bin/startup.sh && qdrouterd -c console.conf" > cmd.sh
CMD ["bash", "cmd.sh"]

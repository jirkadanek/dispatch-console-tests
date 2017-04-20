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

FROM debian:testing
MAINTAINER "jdanek@redhat.com"

RUN apt-get update && apt-get -y install \
    openjdk-8-jre-headless \
    unzip \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TOMCAT_VERSION 8.5.14
ENV HAWTIO_VERSION 1.4.68

RUN mkdir /main
WORKDIR /main

# Download Apache Tomcat
RUN wget http://mirror.hosting90.cz/apache/tomcat/tomcat-8/v$TOMCAT_VERSION/bin/apache-tomcat-$TOMCAT_VERSION.zip && unzip apache-tomcat-$TOMCAT_VERSION.zip && rm apache-tomcat-$TOMCAT_VERSION.zip

# Download prebuilt hawtio
RUN wget https://oss.sonatype.org/content/repositories/public/io/hawt/hawtio-default/$HAWTIO_VERSION/hawtio-default-$HAWTIO_VERSION.war -O /main/apache-tomcat-$TOMCAT_VERSION/webapps/hawtio.war

# Copy the stand-alone console
COPY main/main/qpid-dispatch/console/stand-alone/ /main/apache-tomcat-$TOMCAT_VERSION/webapps/stand-alone/
# Copy the war from build image volume
COPY main/main/qpid-dispatch/console/hawtio/target/dispatch-hawtio-console-*.war /main/apache-tomcat-$TOMCAT_VERSION/webapps/dispatch-hawtio-console.war

RUN chmod +x /main/apache-tomcat-$TOMCAT_VERSION/bin/*.sh
RUN echo "bash /main/apache-tomcat-$TOMCAT_VERSION/bin/catalina.sh run" > tomcat.sh
CMD ["bash", "tomcat.sh"]

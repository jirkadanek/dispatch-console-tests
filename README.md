# dispatch-console-tests
[![Build Status](https://travis-ci.org/jdanekrh/dispatch-console-tests.svg?branch=master)](https://travis-ci.org/jdanekrh/dispatch-console-tests)
Tests for https://github.com/apache/qpid-dispatch/tree/master/console

## Overview

This repository holds end-to-end Webdriver (Selenium 2) tests for dispatch-console.

The console is a Web management tool for Qpid Dispatch Router. It is implemented as a Hawt.io plugin. It displays information about a qpid dispatch router and allows performing administrative commands. Its capabilities are similar to CLI tools `qdstat` and `qdmanage`, except it is a Web page and it can do charts and visualizations. (https://qpid.apache.org/releases/qpid-dispatch-0.6.0/book/console.html)

# README is a work-in-progress. The instructions are how it should work, not how it works right now

## Running

The easiest way to run the tests is to follow `.travis.yml`
* get Firefox 47.0.1 ([47.0 does not work with Selenium](http://seleniumsimplified.com/2016/06/use_selenium_webdriver_jar_locally/)) or Google Chrome
* get the docker image, start it up
* run the tests as per `scripts/travis.sh`

alternatively, run the tests remotely with something like

    pushd webdriver
    py.test -s --driver Remote --capability browserName chrome --host 192.168.33.10 --base-url http://10.0.2.2:8080/hawtio --console-ip 10.0.2.2

You may need to run selenium-server with the following switch

    java -jar ... -Djava.net.preferIPv4Stack=true

## Docker

Docker helps with managing versions. I can test against the same docker image both in Travis CI and locally. See `docker/Dockerfile`.

Version of the docker image, for example `1-abcdef`, is a release number and first six letters from the qpid-dispatch commit hash that was used to build the image, separated by a dash. Docker image is uploaded to hub.docker.com.

    docker build --no-cache .
    docker tag 6e7d0cbcc685 jdanekrh/dispatch-console:2-db8521
    docker push jdanekrh/dispatch-console:2-db8521

Run it with

    docker run -it --rm -p 8080:8080 -p 5673:5673 -p 5672:5672 -v `pwd`:/mnt dispatch-console:...
    
On Travis, binding to `5672` is not possible.

### Useful commands

    # delete all docker images (except running)
    docker rm `docker ps --no-trunc -aq`
    docker rmi $(docker images -q --no-trunc)

## Webdriver

This folder contains Webdriver tests for Dispatch Console. Currently it is very early work.

## py.test

    @pytest.mark.nondestructive

Only tests marked as "nondestructive" get run by default.

    @pytest.mark.reproduces(issue='DISPATCH-428')    
    @pytest.mark.verifies(issue='DISPATCH-428')
    
Current intention is that tests should never be failing, unless there is something wrong with tests themselves or with the CI setup. Tests marked with "reproduces" check for presence of incorrect behavior. When the issue is fixed, test is marked as "verifies" and rewritten to check for correct behavior.

## Random notes

The `-s` switch is sometimes necessary, otherwise py.test suppresses test output (and displays it only for failed tests). The `-n` switch cancels the `-s` switch, apparently.

Tests written in Python 3, mainly because of convenient inline syntax for type annotations

Currently only a standalone router is supported, because Dockerfile doesn't expose ports for connecting more routers and I have yet to learn about Docker networking.

These tests should focus on the console, assuming that OS level differences are caught by other tests for `qdstat`/`qdmanage` and router. These tests can run with the docker image and do not worry about OS on the server. Only OS on clients will be unrolled in the test matrix.

Splitting dispatch container and console/tomcat container might be valuable. Tests will need to restart qdrouterd if they make changes and don't roll them back. 
 Current solution, always undo changes. Ansible cannot be used from Python 3.

## Cache problems in Firefox

In real deployment, people using Firefox may encounter the issue that cached content sticks around in the cache even after dispatch-plugin gets updated. The console then breaks in unexpected ways or does not display altogether. Solution either set cache expiration, or content addressing in urls (file hash or version is part of url). In documentation, recommend clearing the cache in case of problems.



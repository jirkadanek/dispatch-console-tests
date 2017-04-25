# dispatch-console-tests
[![Build Status](https://travis-ci.org/jdanekrh/dispatch-console-tests.svg?branch=master)](https://travis-ci.org/jdanekrh/dispatch-console-tests)
[![Documentation Status](https://readthedocs.org/projects/dispatch-console-tests/badge/?version=latest)](http://dispatch-console-tests.readthedocs.io/en/latest/?badge=latest)

[![SauceLabs Status](https://saucelabs.com/browser-matrix/jdanekrh.svg)](https://saucelabs.com/beta/builds/fdc87f92902c4524800dbdb4eead575f)

![BrowserStack Status](https://www.browserstack.com/automate/badge.svg?badge_key=TksvMTlzR3VHWnZCUGpwOWd5QmRCRi9QU3ZVZkE3NjAzY3JRUWRQMi9xUT0tLTE4cDA4Z1VwUWlpOUQxSGU3YWYxUGc9PQ==--948ecde1b288ba0a070e384141ff4c0a6b4f5e83)

Tests for https://github.com/apache/qpid-dispatch/tree/master/console

## Overview

This repository holds end-to-end Webdriver (Selenium) tests for dispatch-console.

The console is a Web management tool for Qpid Dispatch Router. It is implemented as a Hawtio plugin and also a stand-alone JavaScript webapp. It displays information about a qpid dispatch router and allows performing administrative commands. Its capabilities are similar to CLI tools `qdstat` and `qdmanage`, except it is a Web page and it can do charts and visualizations. (https://qpid.apache.org/releases/qpid-dispatch-0.8.0/book/console.html)

## Running

The easiest way to run the tests is to follow `.travis.yml`
* get the docker images, start them up
* follow either `scripts/firefox.sh` or `scripts/chrome.sh` to setup `geckodriver` or `chromedriver`
* invoke `py.test` as indicated in that `.sh` script

Use the `--console-ip` and `--driver-path` switches of `py.test` to adapt to your situation. That is, if the console has to connect elsewhere than to `localhost` and if driver is not on your `$PATH`.
 
When running with browser on another machine, install `selenium-server` and use something like
 
    py.test -s --driver Remote --capability browserName chrome --host 192.168.33.10 --base-url http://10.0.2.2:8080/hawtio --console-ip 10.0.2.2 --console stand-alone

You may need to run selenium-server with the following switch

    java -Djava.net.preferIPv4Stack=true -jar ... 

## Docker

Docker helps with managing versions. I can test against the same docker image both in Travis CI and locally. See `docker/Dockerfile`.

Version of the docker image, for example `1-abcdef`, is a release number and first six letters from the qpid-dispatch commit hash that was used to build the image, separated by a dash. Docker image is uploaded to hub.docker.com.

Starting from version 4, Docker image is built using what [this blog calls the split-image strategy](https://www.fpcomplete.com/blog/2015/12/docker-split-images). Copy and paste commands from `docker/build.sh` (manually one by one, because there is sudo) to build the build image, run it, then build two run images, `dispatch-console` and `dispatch-router`. Advantage of this approach is smaller size and greater flexibility. Instead of pushing one 1.3 GB image, there is one 205 MB and one 385.5 MB.

    docker tag dispatch-console jdanekrh/dispatch-console:2-db8521
    docker push jdanekrh/dispatch-console:2-db8521

Run it with

    docker run -it --rm -p 8080:8080 -v `pwd`:/mnt jdanekrh/dispatch-console:...
    docker run -it --rm -p 5673:5673 -p 5672:5672 -v `pwd`:/mnt jdanekrh/dispatch-router:...
    
On Travis, binding to `5672` is not possible, so omit that.

### Useful commands

    # prune docker cache
    docker rm `docker ps --no-trunc -aq`
    # delete all docker images (except running)
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

Tests are written in Python 3, mainly because of convenient inline syntax for type annotations.

Currently only a standalone router is supported, because Dockerfile doesn't expose ports for connecting more routers and I have yet to learn about Docker networking.

These tests should focus on the console, assuming that OS level differences are caught by other tests for `qdstat`/`qdmanage` and router. These tests can run in the docker image and do not worry about OS on the server. Only OS and web browser versions on clients will be unrolled in the test matrix.

Splitting dispatch container and console/tomcat container should provevaluable. Tests will need to restart qdrouterd if they make changes and don't roll them back. Current solution, always undo changes. Actually, nothing is yet making any changes, as of now. Ansible cannot be used from Python 3.

Issue tracker on GitHub can be useful as a public todo list just for me. If I enter something there, nobody is going to be running Jira queries over it, chase me about assigning it to sprints and so on.

## Cache problems in Firefox

In real deployment, people using Firefox may encounter the issue that cached content sticks around in the cache even after dispatch-plugin gets updated. The console then breaks in unexpected ways or does not display altogether. Solution either set cache expiration, or content addressing in urls (file hash or version is part of url). In documentation, recommend clearing the cache in case of problems.

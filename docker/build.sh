#!/usr/bin/env bash

# this is to be executed manually, because of sudo
# TODO: there is supposed to be a Docker setting that fixes file permissions...


rm -rf run/console/main
rm -rf run/router/main

# The idea comes from https://www.fpcomplete.com/blog/2015/12/docker-split-images
docker build -t build_dispatch-console --no-cache ./
docker run --rm \
    --volume="$PWD/run/console/main:/console" \
    --volume="$PWD/run/router/main:/router" \
    build_dispatch-console

sudo chown -R jdanek run/console
sudo chown -R jdanek run/router

docker build -t dispatch-console run/console/
docker build -t dispatch-router run/router/

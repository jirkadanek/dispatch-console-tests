#!/usr/bin/env bash
set -ex

# creates images jdanekrh/dispatch-console:latest and jdanekrh/dispatch-router:latest

# this is to be executed manually, because of sudo
# TODO: there is supposed to be a Docker setting that fixes file permissions...

export USERNAME=`whoami`

rm -rf run/console/main || true
rm -rf run/router/main || true

# The idea comes from https://www.fpcomplete.com/blog/2015/12/docker-split-images
docker build -t build_dispatch-console --no-cache ./
docker run --rm \
    --volume="${HOME}/.m2:/root/.m2" \
    --volume="$PWD/run/console/main:/console" \
    --volume="$PWD/run/router/main:/router" \
    build_dispatch-console

sudo chown -R ${USERNAME} run/console
sudo chown -R ${USERNAME} run/router

docker build -t jdanekrh/dispatch-console:latest run/console/
docker build -t jdanekrh/dispatch-router:latest run/router/

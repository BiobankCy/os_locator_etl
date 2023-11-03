#!/bin/sh

docker container rm os_locator_etl_container
docker build -t os_locator_etl .
docker run -p 80:80 -v `pwd`:/app --name os_locator_etl_container os_locator_etl

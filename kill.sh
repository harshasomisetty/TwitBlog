#!/bin/bash

docker kill $(docker ps -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)
docker network prune
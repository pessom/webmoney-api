#!/bin/bash

docker run -it \
	--volume=$(pwd):/app --workdir="/app" --memory=1g --memory-swap=1g --memory-swappiness=0 --entrypoint=/bin/bash python:2.7
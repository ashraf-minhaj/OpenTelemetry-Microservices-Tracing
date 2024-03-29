#!/bin/bash

# VERSION_TAG=$1
# prv stable: v2
VERSION_TAG=v4

cd ../src/service-a

docker buildx create --use --platform=linux/arm64,linux/amd64 --name multiplatform-builder

docker buildx build --platform=linux/arm64,linux/amd64 --push --tag ashraftheminhaj/service-a:$VERSION_TAG .


cd ../service-b
docker buildx build --platform=linux/arm64,linux/amd64 --push --tag ashraftheminhaj/service-b:$VERSION_TAG .

# docker push ashraftheminhaj/hushhub-backend:$1 
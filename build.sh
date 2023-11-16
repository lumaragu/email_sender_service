#!/usr/bin/env bash

DOCKER_TAG=$1

cd app

DOCKER_IMAGE_TAG=gcr.io/$GOOGLE_CLOUD_PROJECT/email-sender:${DOCKER_TAG}

docker build -t $DOCKER_IMAGE_TAG .
docker push $DOCKER_IMAGE_TAG

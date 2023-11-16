#!/usr/bin/env bash

DOCKER_TAG=$1
ENV_FILE=$2

ENV_VARS=$(cat $ENV_FILE | xargs)
export $ENV_VARS

cd app

gcloud run deploy $CLOUD_RUN_SERVICE_NAME \
  --project $GOOGLE_CLOUD_PROJECT \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/email-sender:${DOCKER_TAG} \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars $(echo $ENV_VARS | tr " " ",")

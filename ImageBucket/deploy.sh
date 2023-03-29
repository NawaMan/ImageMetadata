#!/bin/bash

source configurations.sh


aws cloudformation deploy                  \
    --template-file $TEMPLATE_FILE         \
    --stack-name    $STACK_NAME            \
    --parameter-overrides                  \
        ImageBucketName=$IMAGE_BUCKET_NAME \
        ImageTopicName=$IMAGE_TOPIC_NAME   \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

#!/bin/bash

source configurations.sh

LAMBDA_FILE="$IMAGE_LAMBDA_NAME.zip"
LAMBDA_KEY="$IMAGE_LAMBDA_FOLDER/$LAMBDA_FILE"

aws cloudformation deploy                          \
    --stack-name    $STACK_NAME                    \
    --template-file $TEMPLATE_FILE                 \
    --parameter-overrides                          \
        ImageBucketName=$IMAGE_BUCKET_NAME         \
        ImageTopicName=$IMAGE_TOPIC_NAME           \
        ImageTopicArn=$IMAGE_TOPIC_ARN             \
        ImageLambdaBucket=$IMAGE_PROCESS_BUCKET    \
        ImageLambdaKey=$LAMBDA_KEY                 \
        ImageLambdaLayerBucket=$IMAGE_LAYER_BUCKET \
        ImageLambdaLayerKey=$IMAGE_LAYER_KEY       \
    --capabilities                                 \
        CAPABILITY_IAM                             \
        CAPABILITY_NAMED_IAM

#!/bin/bash

STACK_NAME=nawaman-image-process
TEMPLATE_FILE=infrastructure.yml

IMAGE_STACK_NAME=nawaman-image-bucket
IMAGE_BUCKET_NAME=nawaman-images
IMAGE_TOPIC_NAME=nawaman-image-updated


get-image-topic-arn() {
    aws cloudformation describe-stacks\
        --stack-name $IMAGE_STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`ImageTopicArn`].OutputValue' \
        --output text

}
IMAGE_TOPIC_ARN=`get-image-topic-arn`

IMAGE_LAMBDA_NAME=nawaman-image-process
IMAGE_PROCESS_BUCKET=nawaman-lambdas
IMAGE_LAMBDA_FOLDER=nawaman-images

IMAGE_LAYER_BUCKET=nawaman-lambda-layers
IMAGE_LAYER_KEY=layer-pillow.zip

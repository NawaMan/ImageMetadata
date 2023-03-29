#!/bin/bash

# This example create a layer that includes "Pillow" modules.


# Application related configurations
LAYER_CREATOR_STACK=lambda-layer-creator
LAYERS_BUCKET=nawaman-lambda-layers


get-layer-creator-name() {
    aws cloudformation describe-stacks                                                                               \
        --stack-name $LAYER_CREATOR_STACK                                                                            \
        --query 'Stacks[0].Outputs[?ExportName==`'$LAYER_CREATOR_STACK'-CreateLayerLambdaFunctionName`].OutputValue' \
        --output text
}


LAYER_CREATOR_NAME=`get-layer-creator-name`
LAYER_NAME=layer-pillow
LAYER_REQ_PILLOW="Pillow==9.4.0"

aws lambda invoke                         \
    --function-name $LAYER_CREATOR_NAME   \
    --cli-binary-format raw-in-base64-out \
    --output json                         \
    --no-cli-pager                        \
    --payload '{"body":"{\"layer\":\"'$LAYER_NAME'\",\"requirements\": [\"'$LAYER_REQ_PILLOW'\"]}"}' \
    /dev/stdout \
    | jq '.'

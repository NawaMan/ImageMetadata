#!/bin/bash

# This example create a process image lambda.

source configurations.sh


echo "Ensure bucket: s3://$IMAGE_PROCESS_BUCKET"
aws s3api create-bucket             \
    --bucket $IMAGE_PROCESS_BUCKET         \
    --acl bucket-owner-full-control \
    --no-cli-pager
echo ""

echo "Ensure folder: s3://$IMAGE_PROCESS_BUCKET/$IMAGE_LAMBDA_FOLDER/"
aws s3api put-object                \
    --bucket $IMAGE_PROCESS_BUCKET         \
    --key $IMAGE_LAMBDA_FOLDER/           \
    --acl bucket-owner-full-control \
    --no-cli-pager
echo ""


pushd src
LAMBDA_FILE="$IMAGE_LAMBDA_NAME.zip"
LAMBDA_KEY="$IMAGE_LAMBDA_FOLDER/$LAMBDA_FILE"
LAMBDA_S3="s3://$IMAGE_PROCESS_BUCKET/$LAMBDA_KEY"

echo "Zip lambda file: $LAMBDA_FILE"
zip -r $LAMBDA_FILE *

echo "Update lambda file."
aws s3 cp $LAMBDA_FILE $LAMBDA_S3
echo ""

rm $LAMBDA_FILE

popd

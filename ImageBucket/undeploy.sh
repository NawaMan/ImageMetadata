#!/bin/bash

source configurations.sh


aws cloudformation delete-stack --stack-name $STACK_NAME

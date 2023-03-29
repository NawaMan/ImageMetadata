import boto3
import json
import os
import re

from io     import BytesIO
from image  import process_image
from typing import Callable

s3          = boto3.client('s3')
rekognition = boto3.client('rekognition')
sqs         = boto3.client('sqs')


def log(content):
    verbose = (os.environ.get('VERBOSE_MODE', 'quiet') == 'verbose')
    if verbose:
        print(content)


def is_image(key):
    file_extension = re.search(r'\.([a-zA-Z0-9]+)$', key)
    if file_extension:
        file_type = file_extension.group(1)
        log(f"key={key}, file_type={file_type}")
            
        if file_type in ["jpg", "jpeg", "png", "gif"]:
            return True

    return False


def upload(image_bucket, image_key, text):
    s3.upload_fileobj(BytesIO(text.encode('utf-8')), image_bucket, image_key)
    

def process(image_bucket, image_key):
    log(f"Processing: bucket={image_bucket} key={image_key}")

    download_path = '/tmp/{}'.format(os.path.basename(image_key))
    s3.download_file(image_bucket, image_key, download_path)

    save = lambda key, content: upload(image_bucket, key, json.dumps(content, indent=2))

    process_image(image_key, download_path, save)
    
    log(f"Done processing: {image_bucket}/{image_key}")


def handler(event, context):
    log(f"event={json.dumps(event)}")
        
    for event_record in event['Records']:
        event_record_body = event_record['body']
        event_record_body_json = json.loads(event_record_body)
        
        for record in event_record_body_json["Records"]:
            bucket = record['s3']['bucket']['name']
            key    = record['s3']['object']['key']
            
            if not is_image(key):
                continue
            
            try:
                process(bucket, key)
            except Exception as exception:
                print("exception: " + str(exception))
                pass

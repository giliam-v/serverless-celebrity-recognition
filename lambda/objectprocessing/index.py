import json
import logging
# import os
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def handler(event, context):
    logger.debug('Request event:\n%s', json.dumps(event, indent=2, default=str))

    try:
        print('Processing...')

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        logger.info(f'Initiating celebrity recognition for S3 file: {bucket}/{key}')

        response = boto3.client('rekognition').recognize_celebrities(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key,
                }
            }
        )

        logger.info('Response:\n%s', json.dumps(response, indent=2, default=str))
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')
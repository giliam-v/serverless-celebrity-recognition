import json
import logging
import os
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handler(event, context):
    logger.debug('Request event:\n%s', json.dumps(event, indent=2, default=str))

    try:
        print('Hello')
        bucket = os.environ.get('S3Bucket')
        logger.info(f'Upload Bucket: {bucket}')


        url = boto3.client('s3').generate_presigned_url(
            ClientMethod='put_object', 
            Params={'Bucket': bucket, 'Key': 'test'},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "URL": url,
            }),
        }
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye')
    

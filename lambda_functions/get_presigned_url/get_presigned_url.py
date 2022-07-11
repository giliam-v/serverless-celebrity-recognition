import json
import logging
import os
import boto3


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handler(event, context):
    print('Processing...')
    logger.debug('Request event:\n%s', json.dumps(event, indent=2, default=str))

    try:
        bucket = os.environ.get('S3Bucket')
        object = event['queryStringParameters']['filename']

        logger.info(f'Generating pre-signed URL for\n  Bucket: {bucket}\n  Object: {object}')

        url = boto3.client('s3').generate_presigned_url(
            ClientMethod='put_object', 
            Params={'Bucket': bucket, 'Key': object},
            ExpiresIn=3600
        )

        logger.debug(f'Generated pre-signed URL:\n{url}')

        return {
            "statusCode": 200,
            "body": json.dumps({
                "URL": url,
            }),
        }
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')
    

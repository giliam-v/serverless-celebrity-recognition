import json
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def handler(event, context):
    logger.debug('Request event:\n%s', json.dumps(event, indent=2, default=str))

    try:
        print('Hello')
        bucket = os.environ.get('S3Bucket')
        logger.info(f'Upload Bucket: {bucket}')



        return {
            "statusCode": 200,
            "body": json.dumps({
                "Bucket": bucket,
            }),
        }
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye')
    

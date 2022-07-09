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
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        date = event['Records'][0]['eventTime']

        logger.info(f'Initiating celebrity recognition for S3 file: {bucket}/{key}')

        response = boto3.client('rekognition').recognize_celebrities(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key,
                }
            }
        )

        logger.debug('Result:\n%s', json.dumps(response, indent=2, default=str))

        celeb = response['CelebrityFaces'][0]['Name']
        logger.info(f'Celebrity: {celeb}')

        ddbtable = os.environ.get('DDBTable')
        logger.info(f'Writing metadata to table: {ddbtable}')
        
        dbresponse = boto3.client('dynamodb').put_item(TableName=ddbtable, Item={'filename':{'S':key},'date':{'S':date},'celebrity':{'S':celeb}})
        logger.debug('Result:\n%s', json.dumps(dbresponse, indent=2, default=str))


    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')
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
        table = os.environ.get('DDBTable')

        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            filename = record['s3']['object']['key']
            date = record['eventTime']
            
            celeb_names = get_celebrities(bucket, filename)
        
            put_dynamodb_item(table, bucket, filename, date, celeb_names)
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')


def get_celebrities(bucket, filename):
    logger.info(f'Initiating celebrity recognition for S3 image: {bucket}/{filename}')

    response = boto3.client('rekognition').recognize_celebrities(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': filename,
            }
        }
    )
    
    logger.debug('Result:\n%s', json.dumps(response, indent=2, default=str))

    celeb_names = []
    for celeb in response['CelebrityFaces']:
        celeb_names.append(celeb['Name'])

    logger.info(f'Identified celebrities: {celeb_names}')

    return celeb_names


def put_dynamodb_item(table, bucket, filename, date, celeb_names):
    logger.info(f'Writing metadata to table: {table}')

    response = boto3.client('dynamodb').put_item(
        TableName=table,
        Item={
            'bucket':{'S':bucket},
            'filename':{'S':filename},
            'date':{'S':date},
            'celebrities':{'SS':celeb_names}
        }
    )

    logger.debug('Result:\n%s', json.dumps(response, indent=2, default=str))

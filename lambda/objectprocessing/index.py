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
            
            celebrity = get_celebrity(bucket, filename)
        
            put_dynamodb_item(table, filename, date, celebrity)
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')


def get_celebrity(bucket, filename):
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
    celebrities = response['CelebrityFaces']

    if len(celebrities) == 0:
        celebrity = 'unknown'
        logger.info('No celebrities found. Setting name to "unknown"')
    else:
        # For simplicity of demo we only record the first celebrity found
        celebrity = celebrities[0]['Name']
        logger.info(f'Celebrity found: {celebrity}')

    return celebrity


def put_dynamodb_item(table, filename, date, celebrity):
    logger.info(f'Writing metadata to table: {table}')

    response = boto3.client('dynamodb').put_item(
        TableName=table,
        Item={
            'filename':{'S':filename},
            'date':{'S':date},
            'celebrity':{'S':celebrity}
        }
    )

    logger.debug('Result:\n%s', json.dumps(response, indent=2, default=str))

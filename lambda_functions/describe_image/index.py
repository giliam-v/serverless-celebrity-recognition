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
        filename = event['pathParameters']['filename']
        table = os.environ.get('DDBTable')

        logger.info(f'Getting item {filename} from table {table}')

        response = boto3.client('dynamodb').get_item(
            TableName=table,
            Key={
                'filename': {
                    'S': filename,
                }
            }
        )

        logger.debug('Response:\n%s', json.dumps(response, indent=2, default=str))

        return {
            "statusCode": 200,
            "body": json.dumps(response['Item'], indent=2, default=str),
        }
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')
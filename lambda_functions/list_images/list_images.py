import json
import logging
import os
import boto3
import base64

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def handler(event, context):
    print('Processing...')
    logger.debug('Request event:\n%s', json.dumps(event, indent=2, default=str))
    
    try:
        query_strings = event.get('queryStringParameters')
        params = {
            'table': os.environ.get('DDBTable'),
            'bucket': os.environ.get('Bucket'),
        }

        if query_strings:
            params.update(query_strings)


        response_data, token = list_images(**params)
        
        # If pagination is detected we add a NextPage URL in the response data
        if token:
            url = 'https://' + event['requestContext']['domainName'] + event['requestContext']['path']
            response_data['NextPage'] = url + new_query_strings(query_strings, token)

        return {
            "statusCode": 200,
            "body": json.dumps(response_data, indent=2, default=str),
        }
    
    except Exception as e:
        logger.error(str(e))
    
    finally:
        print('Bye!')

def list_images(table, bucket, **kwargs):

    query_params = {
        'TableName': table,
        'IndexName': 'bucket-date-index',
        'KeyConditionExpression': '#B = :bucket',
        'ExpressionAttributeValues': {
            ':bucket': {'S': bucket}
        },
        'ExpressionAttributeNames': {
            "#B":"bucket"
        },
    }

    # Add relevant query parameters  based on querystrings from original request
    if kwargs.get('datetime') == 'ascending':
        query_params['ScanIndexForward'] = True
    elif kwargs.get('datetime') == 'descending':
        query_params['ScanIndexForward'] = False
    
    if kwargs.get('limit'):
        query_params['Limit'] = int(kwargs['limit'])

    if kwargs.get('token'):
        query_params['ExclusiveStartKey'] = decode_token(kwargs['token'])

    logger.debug('Query:\n%s', json.dumps(query_params, indent=2, default=str))

    response = boto3.client('dynamodb').query(**query_params)
    logger.debug('Result:\n%s', json.dumps(response, indent=2, default=str))

    data = {
        'Items': response['Items'],
    }

    # If the response included a LastEvaluatedKey we generate a continuation token for cursor pagination
    if response.get('LastEvaluatedKey'):
        base64_token = encode_token(response['LastEvaluatedKey'])
        logger.info(f'Created pagination token: {base64_token}')
    else:
        base64_token = None

    return (data, base64_token)


def encode_token(last_key):
    json_string = json.dumps(last_key, default=str)
    base64_bytes = base64.b64encode(json_string.encode('utf-8'))
    return base64_bytes.decode()

def decode_token(token):
    decoded_bytes = base64.b64decode(token)
    start_key = json.loads(decoded_bytes)
    return start_key

def new_query_strings(old_query_strings, token):
    new_string = '?'
    # For consistency we need to re-add any query strings that were submitted in original request
    for q in old_query_strings:
        if q == 'token':
            pass
        else:
            new_string += q + '=' + old_query_strings[q] + '&'
    # Append the pagination token query string last
    new_string += 'token' + '=' + token
    return new_string
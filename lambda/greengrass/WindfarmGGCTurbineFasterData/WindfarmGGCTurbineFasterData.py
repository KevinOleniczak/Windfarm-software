import sys
import logging
import json
#import greengrasssdk
import boto3

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = boto3.client('kinesis', region_name='us-west-2')

def WindfarmGGCTurbineFasterData(event, context):

    inbound_topic = context.client_context.custom['subject']

    if not ('deviceID' in event.keys()):
        logger.info('No action found')
        return

    response = client.put_record(
        StreamName='WindfarmDataStream',
        Data=json.dumps(event),
        PartitionKey='tbd'
    )

    return True

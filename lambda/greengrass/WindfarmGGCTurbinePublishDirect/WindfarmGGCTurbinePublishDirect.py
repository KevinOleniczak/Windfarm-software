import sys
import logging
import json
import greengrasssdk
from time import sleep
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')

def WindfarmGGCTurbinePublishDirect(event, context):
    #logger.info(json.dumps(event))

    inbound_topic = context.client_context.custom['subject']

    #if not inbound_topic == command_topic:
    #    logger.info('Inbound topic is not the command topic %s %s', inbound_topic, command_topic)
    #    return

    if not ('turbine_speed' in event.keys()):
        logger.info('No action found')
        return

    response = client.publish(topic='$aws/rules/WindfarmTurbineDataIoTRule', qos=0, payload=json.dumps(event).encode() )

    return True

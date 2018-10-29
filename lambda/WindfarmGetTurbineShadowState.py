import boto3
import json
import datetime
import time

client = boto3.client('iot', region_name='us-west-2')
client2 = boto3.client('iot-data', region_name='us-west-2')

def deviceId2thingName(myDeviceId):
    response = client.list_things(
        #maxResults=1,
        attributeName='deviceId',
        attributeValue=myDeviceId
        #thingTypeName='WindTurbine'
        )
    return response['things'][0]['thingName']

def lambda_handler(event, context):
    if 'thingName' in event:
        myThingName = event['thingName']
    elif 'deviceId' in event:
        myThingName = deviceId2thingName(event["deviceId"])
    else:
        raise

    response = client2.get_thing_shadow(
        thingName=myThingName
        )
    response = json.loads(response['payload'].read())['state']['reported']

    return response

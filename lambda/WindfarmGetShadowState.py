import boto3
import json
import datetime
import time

client = boto3.client('iot', region_name='us-west-2')
client2 = boto3.client('iot-data', region_name='us-west-2')

def lambda_handler(event, context):
    #aDeviceId = event["deviceId"]  #202481602013867
    #print(aDeviceId)

    response = client.list_things(
        maxResults=1,
        #attributeName='deviceId',
        #attributeValue=aDeviceId,
        thingTypeName='WindfarmCore'
        )
    #print (response)
    print(response['things'][0]['thingName'])
    response = client2.get_thing_shadow(
        thingName=response['things'][0]['thingName']
        )
    #print (response)
    response = json.loads(response['payload'].read())['state']['reported']

    return response

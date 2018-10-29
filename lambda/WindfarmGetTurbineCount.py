import boto3
import json
import datetime
import time

client = boto3.client('iot', region_name='us-west-2')
client2 = boto3.client('iot-data', region_name='us-west-2')

def lambda_handler(event, context):

    response = client.list_things(
        maxResults=100,
        thingTypeName='WindfarmTurbine'
        )
    #print (response)

    msg = ""
    aTurbineCnt = 0
    aTurbineConnecedCnt = 0
    aTurbineBrakeOnCnt = 0

    for turbine in response['things']:
        print(turbine['thingName'])
        aTurbineCnt =+ 1
        responseShadow = client2.get_thing_shadow(
            thingName=turbine['thingName']
            )
        shadowStateReported = json.loads(responseShadow['payload'].read())['state']['reported']
        if shadowStateReported['connected'] == "true":
            aTurbineConnecedCnt += 1

        if shadowStateReported['brake_status'] == "ON":
            aTurbineBrakeOnCnt += 1

    #build response message
    msg = {
        "turbine_count": aTurbineCnt,
        "turbine_connected_count": aTurbineConnecedCnt,
        "turbine_brake_on_count": aTurbineBrakeOnCnt
        }

    return msg

import boto3
import json
import datetime
import time
from boto3.dynamodb.conditions import Key, Attr

client = boto3.resource('dynamodb', region_name='us-west-2')
table = client.Table('windturbine-data-latest')

def lambda_handler(event, context):
    #2017-12-18 04:32:00
    if "duration_minutes" not in event:
        aDurationMin = 1
    else:
        aDurationMin = event["duration_minutes"]

    aDeviceId = event["deviceId"] #'202481602013867'
    aTime = (datetime.datetime.utcnow() - datetime.timedelta(minutes=aDurationMin)).strftime("%Y-%m-%d %H:%M:%S")

    #response = table.query(
    #    KeyConditionExpression=Key('deviceID').eq(aDeviceId) & Key('timestamp').gt(aTime)
    #    )
    response = table.query(
        KeyConditionExpression=Key('deviceID').eq(aDeviceId)
        )

    aTot = 0
    aCnt = 0
    for aItem in response['Items']:
        if 'turbine_speed' in aItem:
            aCnt += 1
            aTot += aItem['turbine_speed']

    #build response message
    if aCnt > 0:
        msg = {
            "deviceID": aDeviceId,
            "timestamp": str(aTime),
            "duration_minutes": aDurationMin,
            "turbine_speed": str("%.1f" % round((aTot / aCnt),1)),
            "turbine_voltage": aItem['turbine_voltage'],
            "turbine_temp": aItem['turbine_temp'],
            "turbine_vibe_peak": str("%.0f" % round(aItem['turbine_vibe_peak'], 1)),
            "turbine_vibe_x": aItem['turbine_vibe_x'],
            "turbine_vibe_y": aItem['turbine_vibe_y'],
            "turbine_vibe_z": aItem['turbine_vibe_z']
            }
    else:
        msg = {
            "deviceID": aDeviceId,
            "timestamp": str(aTime),
            "duration_minutes": aDurationMin,
            "turbine_speed": "unknown",
            "turbine_voltage": "unknown",
            "turbine_temp": "unknown",
            "turbine_vibe_peak": "unknown",
            "turbine_vibe_x": "unknown",
            "turbine_vibe_y": "unknown",
            "turbine_vibe_z": "unknown"
            }

    return msg

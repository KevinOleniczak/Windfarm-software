import boto3
import json
import datetime
import time
from boto3.dynamodb.conditions import Key, Attr

client = boto3.resource('dynamodb', region_name='us-west-2')
table = client.Table('windfarm-weather-latest')

def lambda_handler(event, context):
    #2017-12-18 04:32:00
    aWindfarmId = event["windfarmId"]
    aTime = datetime.datetime.utcnow()

    response = table.scan(
        FilterExpression=Attr('timestamp').gt(aTime) and Attr('windfarmId').eq(aWindfarmId)
        )

    aTot = 0
    aCnt = 0
    for aItem in response['Items']:
        if 'wind_speed' in aItem['observation']:
            aCnt += 1
            aTot += float(aItem['observation']['wind_speed'])

    #build response message
    if aCnt > 0:
        msg = {
            "timestamp": str(aTime),
            "latest_wind_speed": str("%.1f" % round((aTot / aCnt),1))
            }
    else:
        msg = {
            "timestamp": str(aTime),
            "latest_wind_speed": "unknown"
            }

    return msg

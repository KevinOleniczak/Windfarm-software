import boto3
import json

client = boto3.client('iot-data')

def lambda_handler(event, context):

    shadow_payload = {
	            "state": {
	                "desired": {
	                    "brake_status": "ON"
	                }
	            }
        }

    client.update_thing_shadow(
        thingName=event['thingName'],
        payload=json.dumps(shadow_payload).encode()
        )

    return 'Brake set'

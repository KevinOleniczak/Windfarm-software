import boto3
import json

client = boto3.client('iot-data')

myClientID = "WindTurbine1"

def lambda_handler(event, context):
    # TODO implement

    shadow_payload = {
	            "state": {
	                "desired": {
	                    "brake_status": "OFF"
	                }
	            }
        }
    client.update_thing_shadow(thingName=myClientID, payload=json.dumps(shadow_payload).encode() )

    return 'Brake reset'

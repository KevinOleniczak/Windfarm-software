import json
import boto3
import base64

ddb_client = boto3.client('dynamodb', region_name='us-west-2')
iota_client = boto3.client('iotanalytics', region_name='us-west-2')

def lambda_handler(event, context):

    msg_buf = []

    #process batch messages
    for index, record in enumerate(event['Records']):

        #Kinesis data is base64 encoded so decode here
        payload=base64.b64decode(record["kinesis"]["data"])
        #print("Decoded payload: " + str(payload))
        payload = json.loads(payload)

        ### DYNAMO DB
        # update ddb
        msg = {
            'deviceID' : {'S':payload['deviceID']},
            'thing_name' : {'S':payload['thing_name']},
            'timestamp' : {'S':payload['timestamp']},
            'loop_cnt' : {'N':str(payload['loop_cnt'])},
            'lat' : {'N':str(payload['lat'])},
            'lng' : {'N':str(payload['lng'])},
            'turbine_temp' : {'N':str(payload['turbine_temp'])},
            'turbine_speed' : {'N':str(payload['turbine_speed'])},
            'turbine_rev_cnt' : {'N':str(payload['turbine_rev_cnt'])},
            'turbine_voltage' : {'N':str(payload['turbine_voltage'])},
            'turbine_vibe_x' : {'N':str(payload['turbine_vibe_x'])},
            'turbine_vibe_y' : {'N':str(payload['turbine_vibe_y'])},
            'turbine_vibe_z' : {'N':str(payload['turbine_vibe_z'])},
            'turbine_vibe_peak' : {'N':str(payload['turbine_vibe_peak'])}
        }

        response = ddb_client.put_item(TableName='windturbine-data-latest', Item=msg)

        #append a msg buffer for the batch put into iot analytics
        msg_buf.append(
            {
                'messageId': str(index),
                'payload': json.dumps(payload)
            }
        )

    ### IOT ANALYTICS
    response = iota_client.batch_put_message(
        channelName='windturbine_data_channel',
        messages=msg_buf
    )

    return {
        'statusCode': 200,
        'body': json.dumps('done')
    }

from __future__ import print_function

import base64
import json

print('Loading function')

def lambda_handler(event, context):
    output = []
    succeeded_record_cnt = 0
    failed_record_cnt = 0

    for record in event['records']:
        print(record['recordId'])
        payload = base64.b64decode(record['data'])
        aDict = json.loads(payload)
        aLine = str(aDict['deviceID']) + ',' + aDict['timestamp'] + ',' + aDict['location'] + ',' + str(aDict['lat']) + ',' + str(aDict['lng']) + ',' + str(aDict['turbine_temp']) + ',' + str(aDict['turbine_speed']) + ',' + str(aDict['turbine_rev_cnt']) + ',' + str(aDict['turbine_voltage']) + ',' + str(aDict['turbine_vibe_x']) + ',' + str(aDict['turbine_vibe_y']) + ',' + str(aDict['turbine_vibe_z']) + '\n'
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(aLine)
        }
        output.append(output_record)
        succeeded_record_cnt = succeeded_record_cnt + 1

    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}

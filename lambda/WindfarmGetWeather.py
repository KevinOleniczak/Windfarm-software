import boto3
import json
import datetime
import time
import csv
import urllib2

client = boto3.client('iotanalytics', region_name='us-west-2')

def lambda_handler(event, context):
    aWindfarmId = event["windfarmId"]

    response = client.get_dataset_content(
        datasetName='windfarm_weather_recent_dataset',
        versionId='$LATEST_SUCCEEDED'
    )

    # csv format is: windfarmid,avg_wind_speed,max_wind_speed
    if response['status']['state'] == 'SUCCEEDED':
        dataset_url = response['entries'][0]['dataURI']
        csv_response = urllib2.urlopen(dataset_url)
        csv_content = list(csv.reader(csv_response))

        for row in csv_content:
            if row[0] == aWindfarmId:
                msg = {
                    "timestamp": row[1],
                    "avg_wind_speed": str("%.1f" % round(float(row[2]),1)),
                    "peak_wind_speed": str("%.1f" % round(float(row[3]),1))
                    }
    else:
        print("no data set ready for recent weather data set")
        msg = {
            "timestamp": str(datetime.datetime.now()),
            "avg_wind_speed": "unknown",
            "peak_wind_speed": "unknown"
            }

    return msg

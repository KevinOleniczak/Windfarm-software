import boto3
from time import sleep
import numbers
import decimal
import csv
import urllib2

client = boto3.client('iotanalytics', region_name='us-west-2')


def lambda_handler(event, context):
    #aWindfarmId = event["windfarmId"]
    aThingName = event["thingName"]

    response = client.get_dataset_content(
        datasetName='windfarm_turbine_recent_dataset',
        versionId='$LATEST_SUCCEEDED'
    )

    # csv format is: deviceid,thingName,avg_turbine_speed,max_turbine_speed,avg_turbine_voltage,max_turbine_voltage,avg_turbine_vibe_peak,max_turbine_vibe_peak,avg_turbine_temp,max_turbine_temp
    if response['status']['state'] == 'SUCCEEDED':
        dataset_url = response['entries'][0]['dataURI']
        csv_response = urllib2.urlopen(dataset_url)
        csv_content = list(csv.reader(csv_response))

        for row in csv_content:
            if row[1] == aThingName:
                msg = {
                    "timestamp": row[2],
                    "avg_turbine_speed": str("%.1f" % round(float(row[3]),1)),
                    "max_turbine_speed": str("%.1f" % round(float(row[4]),1)),
                    "avg_turbine_voltage": str("%.1f" % round(float(row[5]),1)),
                    "max_turbine_voltage": str("%.1f" % round(float(row[6]),1)),
                    "avg_turbine_vibe_peak": str("%.1f" % round(float(row[7]),1)),
                    "max_turbine_vibe_peak": str("%.1f" % round(float(row[8]),1)),
                    "avg_turbine_temp": str("%.1f" % round(float(row[9]),1)),
                    "max_turbine_temp": str("%.1f" % round(float(row[10]),1))
                    }
    else:
        print("no data set ready for recent weather data set")
        msg = {
            "timestamp": str(datetime.datetime.now()),
            "avg_turbine_speed": "unknown",
            "max_turbine_speed": "unknown",
            "avg_turbine_voltage": "unknown",
            "max_turbine_voltage": "unknown",
            "avg_turbine_vibe_peak": "unknown",
            "max_turbine_vibe_peak": "unknown",
            "avg_turbine_temp": "unknown",
            "max_turbine_temp": "unknown"
            }

    return msg
    

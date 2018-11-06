import sys
import logging
import json
import greengrasssdk
from time import sleep
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')
last_wind_speed = -1

while True:
    logger.info("Windfarm is ONLINE")
    #logger.info(json.dumps(event))

    myClientID = "WindfarmGroup_Core"

    f = open('/weather/wind_speed.out', 'r')
    windSpeed = f.read()
    f.close()

    if windSpeed != last_wind_speed:
        msg_payload = {
            "windfarmId": myClientID,
            "timestamp": str(datetime.datetime.utcnow().isoformat()),
            "observation": {
                "wind_speed": windSpeed
            }
        }

        response = client.publish(topic='windfarm-weather', qos=0, payload=json.dumps(msg_payload).encode() )
        last_wind_speed = windSpeed
    sleep(10)

def WindfarmWeatherReporter(event, context):
    #do something here to respond to an event
    return

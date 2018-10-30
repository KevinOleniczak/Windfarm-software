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

    myClientID = "Windfarms_Core"
    
    f = open('/weather/wind_speed.out', 'r')
    windSpeed = f.read()
    f.close()

    msg_payload = {
        "windfarmId": myClientID,
        "timestamp": str(datetime.datetime.utcnow()),
        "observation": {
            "wind_speed": windSpeed
        }
    }
    response = client.publish(topic='windfarm-weather', qos=0, payload=json.dumps(msg_payload).encode() )
    if windSpeed != last_wind_speed:
        response = client.publish(topic='windfarm-weather-latest', qos=0, payload=json.dumps(msg_payload).encode() )
        
        shadow_payload = {
	            "state": {
	                "reported": {
	                    "weather": msg_payload 
	                }
	            }
        }
        client.update_thing_shadow(thingName=myClientID, payload=json.dumps(shadow_payload).encode() )
        
        last_wind_speed = windSpeed
        
    sleep(10)
    
def WindfarmWeatherReporter(event, context):
    #do something here to respond to an event
    return 

import sys
import logging
import json
import greengrasssdk
import platform
#from threading import Timer
import datetime
import os
import numpy as np
import random
#from collections import namedtuple
import cPickle as pickle

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create a greengrass core sdk client
client = greengrasssdk.client('iot-data')
myClientID = "WindTurbine1"

# Retrieve platform information from Greengrass Core
#my_platform = platform.platform()

model_path = '/ml-model-if/home/pi/windfarm'  # Volume path to ML model
model_name = 'turbine-vibe-model.pkl'  # model extracted by GG from zip downloaded from S3

#Load the model
model = None
if os.path.exists(os.path.join(model_path, model_name)):
    with open(os.path.join(model_path, model_name), 'r') as inp:
        model = pickle.load(inp)
        logger.info('MODEL LOADED')
else:
	logger.info('NO MODEL FOUND')

########################################################################

def WindTurbineSafetyCheckIF(event, context):
    logger.info(json.dumps(event))

    if not ('turbine_vibe_peak' in event.keys()):
        logger.info('No action found')
        return

    model
    observation = []
    observation.append(event['turbine_vibe_peak'])
    observation.append(event['turbine_speed'])
    a_observation = np.array([observation])
    pred_result = model.predict(a_observation)
    logger.info(pred_result)

    if pred_result < 0:
        logger.info('Apply brakes!')
        shadow_payload = {
            "state": {
                "desired": {
                    "brake_status": "ON"
                }
            }
        }
        client.update_thing_shadow(thingName=myClientID, payload=json.dumps(shadow_payload).encode() )

    # Let's publish a response back to AWS IoT
    # Only send a message if the button state is 1
    #if (event['key'] == 'ENTER' and event['state'] > 0):
    #    client.publish(topic = "/windturbine-lcd", payload = "Button Pressed")

    return True

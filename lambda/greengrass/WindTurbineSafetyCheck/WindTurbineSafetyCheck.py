import sys
import logging
import json
import greengrasssdk

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')
rpm_threshold = 600
core_shadow_payload = {
	            "state": {
	                "reported": {
	                    "brake_threshold": rpm_threshold
	                }
	            }
        }
client.update_thing_shadow(thingName='WindfarmGroup_Core', payload=json.dumps(core_shadow_payload).encode() )

def WindTurbineSafetyCheck(event, context):
    logger.info("Windfarm Turbine is ONLINE")
    logger.info(json.dumps(event))

    inbound_topic = context.client_context.custom['subject']

    #if not inbound_topic == command_topic:
    #    logger.info('Inbound topic is not the command topic %s %s', inbound_topic, command_topic)
    #    return

    if not ('turbine_speed' in event.keys()):
        logger.info('No action found')
        return

    coreShadow = client.get_thing_shadow(thingName='WindfarmGroup_Core')
    print(coreShadow)
    payloadDict = json.loads(coreShadow['payload'])
    rpm_threshold = payloadDict["state"]["reported"]["brake_threshold"]

    rpm = event['turbine_speed']
    myClientID = "WindTurbine1"
    if rpm > rpm_threshold:
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

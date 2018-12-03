import sys
import logging
import json
import greengrasssdk
import time
import datetime
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')
myClientID = "WindfarmGroup_Core"

last_wind_speed = -1
GPIO_WX_PIN = 37
rpm = 0
mph = 0
elapse = 0
pulse = 0
last_pulse = 0
start_timer = time.time()

def sensorCallback(channel):
  # Called if sensor output changes
  logger.info("callback")
  global pulse, start_timer, elapse, mph
  pulse+=1                                # increase pulse by 1 whenever interrupt occurred
  elapse = time.time() - start_timer      # elapse for every 1 complete rotation made!
  start_timer = time.time()               # let current time equals to start_timer
  mph = calculate_wind_speed()

def calculate_wind_speed():
    global pulse,elapse,rpm,last_pulse
    if elapse !=0:   # to avoid DivisionByZero error
        rpm = 1/elapse * 60
    if pulse == last_pulse:
        rpm = 0
    else:
        last_pulse = pulse
    mph = 2.23694 * (2*rpm*0.0078)      # calculate M/sec
    logger.info("mph")
    return mph

GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIO_WX_PIN , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
GPIO.add_event_detect(GPIO_WX_PIN, GPIO.BOTH, callback=sensorCallback, bouncetime=200)
logger.info("gpio setup done")

while True:
    global mph
    logger.info("looping")
    #if windSpeed != last_wind_speed:
    msg_payload = {
        "windfarmId": myClientID,
        "timestamp": str(datetime.datetime.utcnow().isoformat()),
        "observation": {
            "wind_speed": str(int(round(mph)))
        }
    }

    response = client.publish(topic='windfarm-weather', qos=0, payload=json.dumps(msg_payload).encode() )
    last_wind_speed = str(int(round(mph)))
    time.sleep(10)

def WindfarmWeatherReporterGPIO(event, context):
    #do something here to respond to an event
    return

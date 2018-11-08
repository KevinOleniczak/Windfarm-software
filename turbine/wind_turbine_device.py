from __future__ import division
import logging
import RPi.GPIO as GPIO
from time import sleep
import time, math
import datetime
import json
import uuid
import getopt, sys
from random import randint
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import Adafruit_LSM303
import rgbled as RGBLED

myUUID = str(uuid.getnode())
print(myUUID)

logger = logging.getLogger(__name__)
GPIO.setmode(GPIO.BCM)

# Create a LSM303 instance. Accelerometer
accelerometer = Adafruit_LSM303.LSM303()
# Alternatively you can specify the I2C bus with a bus parameter:
#lsm303 = Adafruit_LSM303.LSM303(busum=2)
accel_x = 0
accel_y = 0
accel_z = 0

#calibration offsets
accel_x_cal = 0
accel_y_cal = 0
accel_z_cal = 0

#run with...
#python wind_turbine_device.py -e 192.168.1.123 -r windturbines_core-ca.txt -c windturbine1-certificate.pem.crt.txt -k windturbine1-private.pem.key
#python wind_turbine_device.py -e a321m91q8py6d4.iot.us-west-2.amazonaws.com -r aws_iot_root_ca.txt -c windturbine1-certificate.pem.crt.txt -k windturbine1-private.pem.key
#python wind_turbine_device.py -e windfarm.awsworkshops.com -r windturbines_core-ca.txt -c windturbine1-certificate.pem.crt.txt -k windturbine1-private.pem.key

#AWS IoT Stuff
myClientID = "WindTurbine1"
myAWSIoTMQTTClient = None
myShadowClient = None
myDeviceShadow = None
useWebsocket = False
host = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""
aws_session = None
myDataSendMode = "normal"
myDataInterval = 5

#Turbine rotation speed sensor
turbine_rotation_sensor_pin = 26 #pin 37
rpm = 0
elapse = 0
pulse = 0
last_pulse = 0
start_timer = time.time()

#Servo control for turbine brake
turbine_servo_brake_pin = 15 #pin 10
GPIO.setwarnings(False)
GPIO.setup(turbine_servo_brake_pin, GPIO.OUT)
brakePWM = GPIO.PWM(turbine_servo_brake_pin, 50)
brake_state = "TBD"
brakePWM.start(3)

GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) 

# ADC MCP3008
# Software SPI configuration:
#import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
CLK  = 11 #pin 23
MISO = 9 #pin 21
MOSI = 10 #pin 19
CS   = 8 #pin 24
#mcp = Adafruit_MCP3008.MCP3008(23, 24, 21, 19)
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

#RGB LED 
redPin   = 5 
greenPin = 6 
bluePin  = 13 

def aws_connect():
    # Init AWSIoTMQTTClient
    global myAWSIoTMQTTClient
    global myShadowClient
    global myDeviceShadow

    if useWebsocket:
        myAWSIoTMQTTClient = AWSIoTMQTTClient(myClientID, useWebsocket=True)
        myAWSIoTMQTTClient.configureEndpoint(host, 443)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath)

        myShadowClient = AWSIoTMQTTShadowClient(myClientID)

    else:
        #myAWSIoTMQTTClient = AWSIoTMQTTClient(myClientID)
        #myAWSIoTMQTTClient.configureEndpoint(host, 8883)
        #myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

        myShadowClient = AWSIoTMQTTShadowClient(myClientID)
        myShadowClient.configureEndpoint(host, 8883)
        myShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
        myAWSIoTMQTTClient = myShadowClient.getMQTTConnection()

    lwt_message = {
            "state": {
                "reported": {
                    "connected":"false"
                }
            }
        }
    myShadowClient.configureLastWill("windfarm-turbines/lwt", json.dumps(lwt_message).encode("utf-8"), 0)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(5)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myAWSIoTMQTTClient.connect()
    #myAWSIoTMQTTClient.subscribe("$aws/...", 1, customCallbackDeltaTest)
    print ("AWS IoT Connected")

    # Shadow config
    myShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myShadowClient.configureMQTTOperationTimeout(10)  # 5 sec
    myShadowClient.connect()
    myDeviceShadow = myShadowClient.createShadowHandlerWithName(myClientID, True)
    myDeviceShadow.shadowRegisterDeltaCallback(myShadowCallbackDelta)

    conn_message = {
            "state": {
                "reported": {
                    "connected":"true"
                }
            }
        }
    myDeviceShadow.shadowUpdate(json.dumps(conn_message).encode("utf-8"), myShadowCallback, 5)
    print ("AWS IoT Shadow Connected")

    myAWSIoTMQTTClient.subscribe("$aws/things/" + myClientID + "/jobs/notify-next", 1, customCallbackJobs)
    print ("AWS IoT Jobs Connected")

def init_turbine_GPIO():                    # initialize GPIO
    global turbine_rotation_sensor_pin
    GPIO.setwarnings(False)
    GPIO.setup(turbine_rotation_sensor_pin, GPIO.IN, GPIO.PUD_UP)
    print ("Turbine is connected")

def init_turbine_brake():
    #global myDeviceShadow
    #myDeviceShadow.shadowDelete(myShadowCallback, 5)
    request_turbine_brake_action("OFF")
    turbine_brake_action("OFF")

def manual_turbine_reset():
    button_state = GPIO.input(21)
    if button_state == True:
        print("Manual brake reset event")
        init_turbine_brake()
        button_state = False


def calculate_turbine_elapse(channel):      # callback function
    global pulse, start_timer, elapse
    pulse+=1                                # increase pulse by 1 whenever interrupt occurred
    elapse = time.time() - start_timer      # elapse for every 1 complete rotation made!
    start_timer = time.time()               # let current time equals to start_timer

def calculate_turbine_speed():
    global pulse,elapse,rpm,last_pulse
    if elapse !=0:   # to avoid DivisionByZero error
        rpm = 1/elapse * 60
    if pulse == last_pulse:
        rpm = 0
    else:
        last_pulse = pulse
    return rpm

def calibrate_turbine_vibe():
    global accel_x_cal, accel_y_cal, accel_z_cal
    # Read the X, Y, Z axis acceleration values and print them.
    accel, mag = accelerometer.read()
    # Grab the X, Y, Z components from the reading and print them out.
    accel_x_cal, accel_y_cal, accel_z_cal = accel
    return 1

def calculate_turbine_vibe():
    global accel_x, accel_y, accel_z, accel_x_cal, accel_y_cal, accel_z_cal
    # Read the X, Y, Z axis acceleration values and print them.
    accel, mag = accelerometer.read()
    # Grab the X, Y, Z components from the reading and print them out.
    accel_x, accel_y, accel_z = accel
    #apply calibration offsets
    accel_x -= accel_x_cal
    accel_y -= accel_y_cal
    accel_z -= accel_z_cal
    #mag_x, mag_z, mag_y = mag
    return 1

def get_turbine_voltage():
    global mcp
    # The read_adc function will get the value of the specified channel (0-7).
    refVal = mcp.read_adc(0)
    calcVolt = round(((3300/1023) * refVal) / 1000, 2)
    return calcVolt

def turbine_brake_action(action):
    global brakePWM,brake_state,myDeviceShadow
    if action == brake_state:
        #thats already the known action state
        #print "Already there"
        return "Already there"

    if action == "ON":
        print "Applying turbine brake!"
        brakePWM.ChangeDutyCycle(11) # turn towards 180 degree
    elif action == "OFF":
        print "Resetting turbine brake."
        brakePWM.ChangeDutyCycle(3)  # turn towards 0 degree
    else:
        return "NOT AN ACTION"
    brake_state = action

    shadow_payload = {
            "state": {
                "reported": {
                    "brake_status": brake_state
                }
            }
        }
    #print shadow_payload
    still_trying = True
    try_cnt = 0
    while still_trying:
        try:
            myDeviceShadow.shadowUpdate(json.dumps(shadow_payload).encode("utf-8"), myShadowCallback, 5)
            still_trying = False
        except:
            try_cnt += 1
            print("Try " + str(try_cnt))
            sleep(1)
            if try_cnt > 10:
                still_trying = False

    return brake_state

def request_turbine_brake_action(action):
    global myDeviceShadow

    if action == "ON":
        RGBLED.redOn
        pass
    elif action == "OFF":
        RGBLED.greenOn
        pass
    else:
        return "NOT AN ACTION"

    new_brake_state = action

    shadow_payload = {
            "state": {
                "desired": {
                    "brake_status": new_brake_state
                }
            }
        }

    still_trying = True
    try_cnt = 0
    while still_trying:
        try:
            myDeviceShadow.shadowUpdate(json.dumps(shadow_payload).encode("utf-8"), myShadowCallback, 5)
            still_trying = False
        except:
            try_cnt += 1
            sleep(1)
            if try_cnt > 10:
                still_trying = False

    return new_brake_state

def process_data_path_changes(param,value):
    global myDeviceShadow

    shadow_payload = {
            "state": {
                "reported": {
                    param: value
                }
            }
        }
    #print shadow_payload
    still_trying = True
    try_cnt = 0
    while still_trying:
        try:
            myDeviceShadow.shadowUpdate(json.dumps(shadow_payload).encode("utf-8"), myShadowCallback, 5)
            still_trying = False
        except:
            try_cnt += 1
            print("Try " + str(try_cnt))
            sleep(1)
            if try_cnt > 10:
                still_trying = False

    return value

def init_turbine_interrupt():
    GPIO.add_event_detect(turbine_rotation_sensor_pin, GPIO.FALLING, callback = calculate_turbine_elapse, bouncetime = 20)

def myShadowCallbackDelta(payload, responseStatus, token):
    global myClientID,myDataSendMode,myDataInterval
    print responseStatus
    print "delta shadow callback >> " + payload

    if responseStatus == "delta/" + myClientID:
        payloadDict = json.loads(payload)
        print "shadow delta >> " + payload
        try:
            if "brake_status" in payloadDict["state"]:
                 turbine_brake_action(payloadDict["state"]["brake_status"])
            if "data_path" in payloadDict["state"]:
                 myDataSendMode = process_data_path_changes("data_path", payloadDict["state"]["data_path"])
            if "data_fast_interval" in payloadDict["state"]:
                 myDataInterval = process_data_path_changes("data_fast_interval", payloadDict["state"]["data_fast_interval"])
        except:
            print "delta cb error"

def myShadowCallback(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    #print responseStatus
    #print "shadow callback >> " + payload

    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        print "shadow accepted"
        #payloadDict = json.loads(payload)
        #print("Update request with token: " + token + " accepted!")
        #print("property: " + str(payloadDict["state"]["desired"]["property"]))
        #print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def customCallbackJobs(payload, responseStatus, token):
    global myClientID,myDataSendMode,myDataInterval
    print responseStatus
    print "Next job callback >> " + payload

    if responseStatus == "delta/" + myClientID:
        payloadDict = json.loads(payload)
        print "shadow delta >> " + payload
        try:
            if "brake_status" in payloadDict["state"]:
                 turbine_brake_action(payloadDict["state"]["brake_status"])
            if "data_path" in payloadDict["state"]:
                 myDataSendMode = process_data_path_changes("data_path", payloadDict["state"]["data_path"])
            if "data_fast_interval" in payloadDict["state"]:
                 myDataInterval = process_data_path_changes("data_fast_interval", payloadDict["state"]["data_fast_interval"])
        except:
            print "delta cb error"
def evaluate_turbine_safety():
    global rpm
    if rpm > 20:
        request_turbine_brake_action("ON")
    #else:
    #    turbine_brake_action("OFF")

def main():
    global myClientID,rpm,pulse,myAWSIoTMQTTClient,myShadowClient,myDeviceShadow,myDataSendMode,myDataInterval
    RGBLED.blueOn 
    my_loop_cnt = 0
    last_reported_speed = -1
    try:
        aws_connect()
        init_turbine_GPIO()
        init_turbine_interrupt()
        sleep(5)
        init_turbine_brake()
        calibrate_turbine_vibe()
        print "Turbine Monitoring Starting..."
        RGBLED.blueOff
        RGBLED.greenOn
        while True:
            calculate_turbine_speed()
            #evaluate_turbine_safety()
            calculate_turbine_vibe()
            my_loop_cnt += 1

            myReport = {
                'deviceID' : myUUID,
                'thing_name' : myClientID,
                'timestamp' : str(datetime.datetime.utcnow().isoformat()),
                'loop_cnt' : str(my_loop_cnt),
                'location' : "ORD10-14",
                'lat' : 42.888,
                'lng' : -88.123,
                'turbine_temp' : 75, #randint(65,90),  #temp fix
                'turbine_speed' : rpm,
                'turbine_rev_cnt' : pulse,
                'turbine_voltage' : str(get_turbine_voltage()),
                'turbine_vibe_x' : accel_x,
                'turbine_vibe_y' : accel_y,
                'turbine_vibe_z' : accel_z
            }
            try:
                print('rpm:{0:.0f}-RPM pulse:{1} accel-x:{2} accel-y:{3} accel-z:{4} brake:{5} cnt:{6} voltage:{7}'.format(rpm,pulse,accel_x, accel_y, accel_z,brake_state,str(my_loop_cnt),str(get_turbine_voltage())))
                if rpm > 0 or last_reported_speed != 0:
                     if myDataSendMode == "fast":
                         myTopic = "windturbine-data-fast"
                     else:
                         myTopic = "windturbine-data"

                     last_reported_speed = rpm
                     myAWSIoTMQTTClient.publish(myTopic, json.dumps(myReport), 0)
          
            except:
                logger.warning("exception while publishing")
                raise

            manual_turbine_reset()

            if myDataSendMode == "fast":
                 sleep(myDataInterval)
            else:
                 sleep(10)

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("Disconnecting AWS IoT")
        conn_message = {
            "state": {
                "reported": {
                    "connected":"false"
                }
            }
        }
        myDeviceShadow.shadowUpdate(json.dumps(conn_message).encode("utf-8"), myShadowCallback, 5)
        sleep(1)
        myShadowClient.disconnect()
        sleep(2)
        print ("Done.\nExiting.")

if __name__ == "__main__":

    # Usage
    usageInfo = """Usage:

    Use certificate based mutual authentication:
    python someprogram.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

    Use MQTT over WebSocket:
    python someprogram.py -e <endpoint> -r <rootCAFilePath> -w

    Type "python someprogram.py -h" for available options.
    """
    # Help info
    helpInfo = """-e, --endpoint
            Your AWS IoT custom endpoint
    -r, --rootCA
            Root CA file path
    -c, --cert
            Certificate file path
    -k, --key
            Private key file path
    -w, --websocket
            Use MQTT over WebSocket
    -h, --help
            Help information

    """

    # Read in command-line parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:", ["help", "endpoint=", "key=","cert=","rootCA=", "websocket"])
        if len(opts) == 0:
            raise getopt.GetoptError("No input parameters!")
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(helpInfo)
                exit(0)
            if opt in ("-e", "--endpoint"):
                host = arg
            if opt in ("-r", "--rootCA"):
                rootCAPath = arg
            if opt in ("-c", "--cert"):
                certificatePath = arg
            if opt in ("-k", "--key"):
                privateKeyPath = arg
            if opt in ("-w", "--websocket"):
                useWebsocket = True
    except getopt.GetoptError:
            print(usageInfo)
            exit(1)

    # Missing configuration notification
    missingConfiguration = False
    if not host:
        print("Missing '-e' or '--endpoint'")
        missingConfiguration = True
    if not rootCAPath:
        print("Missing '-r' or '--rootCA'")
        missingConfiguration = True
    if not useWebsocket:
        if not certificatePath:
            print("Missing '-c' or '--cert'")
            missingConfiguration = True
        if not privateKeyPath:
            print("Missing '-k' or '--key'")
            missingConfiguration = True
    if missingConfiguration:
        exit(2)

    logging.basicConfig(filename='wind_turbine_device.log',level=logging.INFO,format='%(asctime)s %(message)s')
    logger.info("Welcome to the AWS Windfarm Turbine Device Reporter.")
    main()

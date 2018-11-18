#!/usr/bin/python

# Import required libraries
import time
import datetime
import RPi.GPIO as GPIO

rpm = 0
mph = 0
elapse = 0
pulse = 0
last_pulse = 0
start_timer = time.time()

def calculate_wind_speed():
    global pulse,elapse,rpm,last_pulse,mph
    if elapse !=0:   # to avoid DivisionByZero error
        rpm = 1/elapse * 60
    if pulse == last_pulse:
        rpm = 0
    else:
        last_pulse = pulse
    mph = 2.23694 * (2*rpm*0.0078)      # calculate M/sec
    return rpm

def sensorCallback(channel):
  # Called if sensor output changes
  global rpm, pulse, start_timer, elapse, mph
  pulse+=1                                # increase pulse by 1 whenever interrupt occurred
  elapse = time.time() - start_timer      # elapse for every 1 complete rotation made!
  start_timer = time.time()               # let current time equals to start_timer
  calculate_wind_speed()

  #if GPIO.input(channel):
    # No magnet
    #print("Sensor HIGH " + str(mph))
  #else:
    # Magnet
    #print("Sensor LOW " + str(mph))

def main():
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.
  global mph
  try:
    # Loop until users quits with CTRL-C
    f = open('/weather/wind_speed.out', 'w')
    while True :
      time.sleep(0.1)
      f.truncate()
      f.seek(0)
      f.write(str(int(round(mph))))
      #f.write (print("%.0f" % mph))
      f.flush()
      #print(str(mph))

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BOARD)

print("Setup GPIO pin as input on GPIO37")

# Set Switch GPIO as input
# Pull high by default
GPIO.setup(37 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(37, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

if __name__=="__main__":
   main()

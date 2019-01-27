 #!/usr/bin/python
# Import required libraries
import sys
import time
import RPi.GPIO as GPIO
import requests
import json
from websocket import create_connection


# Use BCM GPIO references
# instead of physical pin numbers
dispenser_id = 1
server_url = "mighty-wildwood-93572.herokuapp.com"

def dispense():
        GPIO.setmode(GPIO.BCM)
         

        # Define GPIO signals to use
        # Physical pins 11,15,16,18
        # GPIO17,GPIO22,GPIO23,GPIO24
        StepPins = [17,22,23,24]

        # Set all pins as output
        for pin in StepPins:
                GPIO.setup(pin,GPIO.OUT)
                GPIO.output(pin, False)

        # Define advanced sequence
        # as shown in manufacturers datasheet
        Seq = [[1,0,0,1],
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1]]
            
        StepCount = len(Seq)
        StepDir = 1 # Set to 1 or 2 for clockwise
                # Set to -1 or -2 for anti-clockwise

        if len(sys.argv)>1:
          WaitTime = int(sys.argv[1])/float(1000)
        else:
          WaitTime = 2/float(1000)
         
        # Initialise variables
        StepCounter = 0
        # Start main loop
        timeout = time.time() + 10
        while time.time() < timeout:
         
          print("Dispensing")
         
          for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
              GPIO.output(xpin, True)
            else:
              GPIO.output(xpin, False)
         
          StepCounter += StepDir
         
          # If we reach the end of the sequence
          # start again
          if (StepCounter>=StepCount):
            StepCounter = 0
          if (StepCounter<0):
            StepCounter = StepCount+StepDir
         
          # Wait before moving on
          time.sleep(WaitTime)
        requests.post("https://{server_url}/dispensed/{dispenser_id}/".format(server_url = server_url, dispenser_id = dispenser_id))

print("ws://{server_url}/ws/dispenser/{dispenser_id}/".format(server_url = server_url, dispenser_id = dispenser_id))

ws = create_connection("ws://{server_url}/ws/dispenser/{dispenser_id}/".format(server_url = server_url, dispenser_id = dispenser_id))

while True:
	result =  json.loads(ws.recv())
	print(result)
	if("text" in result["dispenser"] and result["dispenser"]["text"] == dispenser_id):
    		dispense()

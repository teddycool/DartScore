import time

import RPi.GPIO as GPIO

from Actuators import LedIndicator
from DartScoreMainConfig import dartconfig
from Inputs import IoInputs

#Start...

GPIO.setmode(GPIO.BCM)
calButton = IoInputs.PushButton(GPIO ,dartconfig["IO"]["CalButton"])
gameButton = IoInputs.PushButton(GPIO ,dartconfig["IO"]["GameButton"])
playerSwitch = IoInputs.OnOnSwitch(GPIO, dartconfig["IO"]["GameSwitch1"] ,dartconfig["IO"]["GameSwitch2"])

calButton.initialize()
gameButton.initialize()
playerSwitch.initialize()

onLed =  LedIndicator.LedIndicator(GPIO, dartconfig["IO"]["OnLed"])
calLed = LedIndicator.LedIndicator(GPIO, dartconfig["IO"]["CalLed"])
gameLed = LedIndicator.LedIndicator(GPIO, dartconfig["IO"]["GameLed"])
hitLed = LedIndicator.LedIndicator(GPIO, dartconfig["IO"]["HitLed"])
print "Start testing...."
print "OnLed... On"
onLed.activate(True)
time.sleep(0.5)

print "CalLed... On"
calLed.activate(True)
time.sleep(0.5)

print "GameLed... On"
gameLed.activate(True)
time.sleep(0.5)

print "HitLed... On"
hitLed.activate(True)
time.sleep(0.5)

running = True
while(running):
    try:
        print "CalButtonState: " + str(calButton.update())
        print "GameButtonState: " + str(gameButton.update())
        print "PlayerSwitchState" + str(playerSwitch.update())
        time.sleep(0.2)
    except:
        running= False

GPIO.cleanup()
print "Test is done..."







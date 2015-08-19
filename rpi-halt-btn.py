# import required libraries
import RPi.GPIO as GPIO
import subprocess, time

# setup the GPIO pins for the halt switch
HALT_SWITCH_GPIO_PIN = 24
HALT_SWITCH_LED_GPIO_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALT_SWITCH_LED_GPIO_PIN, GPIO.OUT)
GPIO.setup(HALT_SWITCH_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(HALT_SWITCH_LED_GPIO_PIN, True)

print "rpi-halt-btn: started and now waiting for GPIO halt button to be pressed."

# wait for the button to be pressed and when pressed, issue
# the halt command to stop the raspberry pi
try:
	GPIO.wait_for_edge(HALT_SWITCH_GPIO_PIN, GPIO.FALLING)
except KeyboardInterrupt:
	print "Stopped by user"
	GPIO.cleanup()
print "rpi-internet-monitor: Shutdown switch pressed - halting system."
GPIO.output(HALT_SWITCH_LED_GPIO_PIN, False)
time.sleep(0.5)
GPIO.output(HALT_SWITCH_LED_GPIO_PIN, True)
subprocess.call(["sudo","halt"])

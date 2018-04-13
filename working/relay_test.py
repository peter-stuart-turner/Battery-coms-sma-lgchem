import RPi.GPIO as GPIO
import time

testPin = 4
GPIO.setmode(GPIO.BCM)

GPIO.setup(testPin, GPIO.OUT)

while True:
	GPIO.output(testPin, GPIO.LOW)
	time.sleep(1)
	GPIO.output(testPin, GPIO.HIGH)
	time.sleep(0.5)



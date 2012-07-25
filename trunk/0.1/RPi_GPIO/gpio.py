import RPi.GPIO as GPIO

# to use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)

# set up GPIO output channel
GPIO.setup(12, GPIO.OUT)

# set RPi board pin 12 high
GPIO.output(12, GPIO.HIGH)

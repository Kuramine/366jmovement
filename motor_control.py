# Author: Yujie Hou
# Last Edit: 11/17/2017

from msvcrt import getch # keyboard input
import sys
import time
import RPi.GPIO as GPIO
#from multiprocessing import Process

mode=GPIO.getmode()
GPIO.cleanup()

# assigning; GPIO pin setup
Forward = 26 # motor 1 forward
Backward = 20 # motor 1 backward
Forward2 = 19 # motor 2 forward
Backward2 = 16 # motor 2 backward
sleeptime=1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Forward2, GPIO.OUT)
GPIO.setup(Backward2, GPIO.OUT)

def forward(x):
    GPIO.output(Forward, GPIO.HIGH) # motor 1 forward activate
    GPIO.output(Forward2, GPIO.HIGH) # motor 2 forward activate
    print("forward")
    time.sleep(x) # wait x amount of time
    GPIO.output(Forward, GPIO.LOW) # motor 1 forward deactivate
    GPIO.output(Forward2, GPIO.LOW) # motor 2 forward deactivate

def reverse(x):
    GPIO.output(Backward, GPIO.HIGH)
    GPIO.output(Backward2, GPIO.HIGH)
    print("reverse")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)
    GPIO.output(Backward2, GPIO.LOW)

def left(x):
    GPIO.output(Backward, GPIO.HIGH) # left motor backward
    GPIO.output(Forward2, GPIO.HIGH) # right motor forward
    print("left")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)
    GPIO.output(Forward2, GPIO.LOW)

def right(x):
    GPIO.output(Forward, GPIO.HIGH)
    GPIO.output(Backward2, GPIO.HIGH)
    print("right")
    time.sleep(x)
    GPIO.output(Forward, GPIO.LOW)
    GPIO.output(Backward2, GPIO.LOW)

while (1): # forever loop
    key = ord(getch()) # detect key being pressed
    print(ord(getch())) # print key being pressed
    
    if key == 3: #3 = ctrl+c to break out of forever loop
        break

    if key == 119: #119 = 'w' move forward
        forward(1)
        
    if key == 97: #97 = 'a' turn left
        left(1)

    if key == 115: #115 = 's' move backward
        reverse(1)

    if key == 100: #100 = 'd' turn right
        right(1)

GPIO.cleanup()
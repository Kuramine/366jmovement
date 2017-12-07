# Author: Yujie Hou
# Last Edit: 11/30/2017

from calculations import calculate_xy_position, calculate_xy_shift
import sys, time
import math, random
import pygame
import RPi.GPIO as GPIO

##### PYGAME INITIALIZATION #####
pygame.init()

# colors
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
# screen size, car size
screen_height = 1000
screen_width = 1000
car_width = 96 #pixel size of sprite
car_height = 96
car_position = [500,500]

# orientation of car
car_angle = 90
travel_distance = 20
turn_angle = 15

sleeptime=1

sensor_list = [] # holds all point Objects of type list[x,y]
sensor_list2 = [] # left sensor
sensor_list3 = [] # right sensor
history_list = [] # holds all points of past position of car

gameDisplay = pygame.display.set_mode((screen_height,screen_width))
car_surface = pygame.image.load('car_body.jpg')
start_surface = pygame.image.load('start.jpg')
arrow_surface = pygame.image.load('arrowKeys.jpg')# assign as arrowkeys as default

pygame.display.set_caption('Motor test')

gameExit = False

##### GPIO INITIALIZATION #####

mode=GPIO.getmode()
GPIO.cleanup()

# assigning; GPIO pin setup
Forward = 20 # motor 1 forward
Backward = 26 # motor 1 backward
Forward2 = 19 # motor 2 forward
Backward2 = 16 # motor 2 backward
sleeptime=1

GPIO.setmode(GPIO.BCM)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Forward2, GPIO.OUT)
GPIO.setup(Backward2, GPIO.OUT)

##### ULTRASONIC GPIO INITIALIZATION #####

GPIO_TRIGGER = 23
GPIO_ECHO = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

##### CALCULATIONS OF POSITION #####

def rot_center(image, angle):
    #rotate an image while keeping its center and size
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

car_surface = rot_center(car_surface, car_angle) # initial rotation on first load of car sprite
history_list.append([car_position[0],car_position[1]]) # initial start_point for history

def calculate_position(distance, direction): # calculate sensed object position relative to car, 2 scenarios with 4 quadrants each = 8 conditions
    if direction == "forward":
        movement = calculate_xy_shift(travel_distance, car_angle) # returns how far all dots should move relative to car
        #print(movement)
        #print(car_angle)
        for item in sensor_list:
            item[0]-=movement[0]
            item[1]+=movement[1]
        
        for item in history_list:
            item[0]-=movement[0]
            item[1]+=movement[1]

        history_list.append([car_position[0],car_position[1]]) 

    if direction == "backward":
        movement = calculate_xy_shift(travel_distance, car_angle) # returns how far all dots should move relative to car
        #print(movement)
        #print(car_angle)
        for item in sensor_list:
            item[0]+=movement[0]
            item[1]-=movement[1]

        for item in history_list:
            item[0]+=movement[0]
            item[1]-=movement[1]

        history_list.append([car_position[0],car_position[1]])

    new_point = calculate_xy_position(distance, car_angle) # position of a new point
    sensor_list.append([car_position[0]+new_point[0],car_position[1]-new_point[1]]) # add new point
    #history_list.append([car_position[0],car_position[1]]) # add history point
    # moved to within forward/backward to prevent duplicate history points when turning

def fake_sensor():
    travel_time = random.randint(300,350)
    return travel_time
    # decrease movement sleep times for more readings

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return int(distance*2) #set arbitrary scale, convert to integer  

def change_angle(turn_angle):
    global car_angle
    car_angle+=turn_angle
    if car_angle>360:
        car_angle-=360
    if car_angle<0:
        car_angle+=360

##### END CALCULATIONS #####

def forward(x):
    GPIO.output(Forward, GPIO.HIGH) # motor 1 forward activate
    GPIO.output(Forward2, GPIO.HIGH) # motor 2 forward activate
    print("forward")
    time.sleep(x) # wait x amount of time
    GPIO.output(Forward, GPIO.LOW) # motor 1 forward deactivate
    GPIO.output(Forward2, GPIO.LOW) # motor 2 forward deactivate
    calculate_position(distance(),'forward')

def reverse(x):
    GPIO.output(Backward, GPIO.HIGH)
    GPIO.output(Backward2, GPIO.HIGH)
    print("reverse")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)
    GPIO.output(Backward2, GPIO.LOW)
    calculate_position(distance(),'backward')

def left(x):
    GPIO.output(Backward, GPIO.HIGH) # left motor backward
    GPIO.output(Forward2, GPIO.HIGH) # right motor forward
    print("left")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)
    GPIO.output(Forward2, GPIO.LOW)
    change_angle(turn_angle)
    global car_surface
    car_surface = rot_center(pygame.image.load('car_body.jpg'), car_angle) 
    # redefining a new surface every time as a new image removes artifacting when rotating
    calculate_position(distance(),'left')

def right(x):
    GPIO.output(Forward, GPIO.HIGH)
    GPIO.output(Backward2, GPIO.HIGH)
    print("right")
    time.sleep(x)
    GPIO.output(Forward, GPIO.LOW)
    GPIO.output(Backward2, GPIO.LOW)
    change_angle(-turn_angle)
    global car_surface
    car_surface = rot_center(pygame.image.load('car_body.jpg'), car_angle)
    calculate_position(distance(),'right')

while not gameExit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
    
    gameDisplay.fill(black)

    # detecting key presses and calling motors
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]:
       forward(.5)
    if pressed[pygame.K_a]:
       left(.1)
    if pressed[pygame.K_s]:
       reverse(.5)
    if pressed[pygame.K_d]:
       right(.1)

    gameDisplay.blit(start_surface,[history_list[0][0]-10,history_list[0][1]-10,20,20]) # displaying start point 
    gameDisplay.blit(car_surface,[screen_width/2-car_width/2,screen_height/2-car_height/2,car_width,car_height]) # displaying car
    gameDisplay.blit(arrow_surface,[0,0,288,187])
    # drawing the dots
    
    for item in sensor_list:
        gameDisplay.fill(white, rect=[item[0],item[1],5,5]) #Dots are size 5x5
    for item in history_list:
        gameDisplay.fill(green, rect=[item[0],item[1],5,5])

    pygame.display.update()
    time.sleep(.5)

pygame.quit()
GPIO.cleanup()
quit()

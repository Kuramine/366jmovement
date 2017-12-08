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
GPIO_TRIGGER2 = 14
GPIO_ECHO2 = 15
GPIO_TRIGGER3 = 17
GPIO_ECHO3 = 27

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)
GPIO.setup(GPIO_TRIGGER3, GPIO.OUT)
GPIO.setup(GPIO_ECHO3, GPIO.IN)

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

def calculate_position(distance, distance2, distance3, direction): # calculate sensed object position relative to car, 2 scenarios with 4 quadrants each = 8 conditions
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

    if distance!=1000: # 1000 means error
        new_point = calculate_xy_position(distance, car_angle) # position of a new point
        sensor_list.append([car_position[0]+new_point[0],car_position[1]-new_point[1]]) # add new point
    if distance2!=1000:
        new_point = calculate_xy_position(distance2, car_angle-90) # position of a new left point
        sensor_list.append([car_position[0]+new_point[0],car_position[1]-new_point[1]])
    if distance3!=1000:
        new_point = calculate_xy_position(distance3, car_angle+90) # position of a new right point
        sensor_list.append([car_position[0]+new_point[0],car_position[1]-new_point[1]]) 
    #history_list.append([car_position[0],car_position[1]]) # add history point
    # moved to within forward/backward to prevent duplicate history points when turning

def fake_sensor():
    travel_time = random.randint(300,350)
    return travel_time
    # decrease movement sleep times for more readings

def distance():
    if GPIO.input (GPIO_ECHO):                                          # If the 'Echo' pin is already high
        return (1000)                                                   # then exit with 1000 (sensor fault)
    distance = 0                                                        # Set initial distance to zero
    GPIO.output (GPIO_TRIGGER,False)                                    # Ensure the 'Trig' pin is low for at
    time.sleep (0.05)                                                   # least 50mS (recommended re-sample time)
    GPIO.output (GPIO_TRIGGER,True)                                     # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0                                                  # No need to use the 'time' module here,
    dummy_variable = 0                                                  # a couple of 'dummy' statements will do fine
    GPIO.output (GPIO_TRIGGER,False)                                    # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()                             # Set inital time values to current time
    while not GPIO.input (GPIO_ECHO):                                   # Wait for the start of the 'Echo' pulse
        time1 = time.time()                                             # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:                                        # If the 'Echo' pin doesn't go high after 20mS
            distance = 1000                                             # then set 'distance' to 1000
            break                                                       # and break out of the loop   
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 1000 (sensor fault)
    while GPIO.input (GPIO_ECHO):                                       # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()                                             # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:                                        # If the 'Echo' pin doesn't go low after 20mS
            distance = 1000                                             # then ignore it and set 'distance' to 1000
            break                                                       # and break out of the loop    
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 100 (sensor fault)
    distance = (time2 - time1) / 0.00000295 / 2 / 10                    # Convert the timer values into centimetres
    return (distance)                                                   # Exit with the distance in centimetres

def distance2():
    if GPIO.input (GPIO_ECHO2):                                          # If the 'Echo' pin is already high
        return (1000)                                                   # then exit with 1000 (sensor fault)
    distance = 0                                                        # Set initial distance to zero
    GPIO.output (GPIO_TRIGGER2,False)                                    # Ensure the 'Trig' pin is low for at
    time.sleep (0.05)                                                   # least 50mS (recommended re-sample time)
    GPIO.output (GPIO_TRIGGER2,True)                                     # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0                                                  # No need to use the 'time' module here,
    dummy_variable = 0                                                  # a couple of 'dummy' statements will do fine
    GPIO.output (GPIO_TRIGGER2,False)                                    # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()                             # Set inital time values to current time
    while not GPIO.input (GPIO_ECHO2):                                   # Wait for the start of the 'Echo' pulse
        time1 = time.time()                                             # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:                                        # If the 'Echo' pin doesn't go high after 20mS
            distance = 1000                                             # then set 'distance' to 1000
            break                                                       # and break out of the loop   
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 1000 (sensor fault)
    while GPIO.input (GPIO_ECHO2):                                       # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()                                             # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:                                        # If the 'Echo' pin doesn't go low after 20mS
            distance = 1000                                             # then ignore it and set 'distance' to 1000
            break                                                       # and break out of the loop    
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 100 (sensor fault)
    distance = (time2 - time1) / 0.00000295 / 2 / 10                    # Convert the timer values into centimetres
    return (distance)                                                   # Exit with the distance in centimetres

def distance3():
    if GPIO.input (GPIO_ECHO3):                                          # If the 'Echo' pin is already high
        return (1000)                                                   # then exit with 1000 (sensor fault)
    distance = 0                                                        # Set initial distance to zero
    GPIO.output (GPIO_TRIGGER3,False)                                    # Ensure the 'Trig' pin is low for at
    time.sleep (0.05)                                                   # least 50mS (recommended re-sample time)
    GPIO.output (GPIO_TRIGGER3,True)                                     # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0                                                  # No need to use the 'time' module here,
    dummy_variable = 0                                                  # a couple of 'dummy' statements will do fine
    GPIO.output (GPIO_TRIGGER3,False)                                    # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()                             # Set inital time values to current time
    while not GPIO.input (GPIO_ECHO3):                                   # Wait for the start of the 'Echo' pulse
        time1 = time.time()                                             # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:                                        # If the 'Echo' pin doesn't go high after 20mS
            distance = 1000                                             # then set 'distance' to 1000
            break                                                       # and break out of the loop   
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 1000 (sensor fault)
    while GPIO.input (GPIO_ECHO3):                                       # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()                                             # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:                                        # If the 'Echo' pin doesn't go low after 20mS
            distance = 1000                                             # then ignore it and set 'distance' to 1000
            break                                                       # and break out of the loop    
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 100 (sensor fault)
    distance = (time2 - time1) / 0.00000295 / 2 / 10                    # Convert the timer values into centimetres
    return (distance)                                                   # Exit with the distance in centimetres

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
    calculate_position(distance(),distance2(),distance3(),'forward')

def reverse(x):
    GPIO.output(Backward, GPIO.HIGH)
    GPIO.output(Backward2, GPIO.HIGH)
    print("reverse")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)
    GPIO.output(Backward2, GPIO.LOW)
    calculate_position(distance(),distance2(),distance3(),'backward')

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
    calculate_position(distance(),distance2(),distance3(),'left')

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
    calculate_position(distance(),,distance2(),distance3(),'right')

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
    #time.sleep(.5)

pygame.quit()
GPIO.cleanup()
quit()

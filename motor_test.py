# Author: Yujie Hou
# Last Edit: 11/30/2017

from calculations import calculate_xy_position, calculate_xy_shift
import sys, time, math
import random
import pygame

pygame.init()

# colors
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
# screen size, car size
screen_height = 1000
screen_width = 1000
car_width = 40 #pixel size of sprite
car_height = 40
car_position = [500,500]

# orientation of car
car_angle = 90
travel_distance = 20
turn_angle = 36

sleeptime=1

sensor_list = [] # holds all point Objects of type list[x,y]
sensor_list2 = [] # left sensor
sensor_list3 = [] # right sensor
history_list = [] # holds all points of past position of car
sensor_data = [0,0,0] #holds 3 readings

gameDisplay = pygame.display.set_mode((screen_height,screen_width))
car_surface = pygame.image.load('car_body.jpg')
start_surface = pygame.image.load('start.jpg')
arrow_surface = pygame.image.load('WASD_Keys.jpg')# assign as arrowkeys as default
myfont = pygame.font.SysFont('Comic Sans MS', 30)
scale_surface = pygame.image.load('scale.jpg')

pygame.display.set_caption('Motor test')

gameExit = False

##### calculations #####

# rot_center was obtained from official github wiki
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

car_surface = rot_center(car_surface, car_angle) # initial rotation on first load of car sprite
history_list.append([car_position[0],car_position[1]]) # initial start_point for history

def calculate_position(distance,distance2,distance3, direction): # calculate sensed object position relative to car, 2 scenarios with 4 quadrants each = 8 conditions
    global sensor_data
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
    new_point2 = calculate_xy_position(distance, car_angle+90) # position of new right point
    new_point3 = calculate_xy_position(distance, car_angle-90) # position of new right point
    sensor_list.append([car_position[0]+new_point[0],car_position[1]-new_point[1]]) # add new point
    #sensor_list.append([car_position[0]+new_point2[0],car_position[1]-new_point2[1]]) # add new point left
    #sensor_list.append([car_position[0]+new_point3[0],car_position[1]-new_point3[1]]) # add new point right

    sensor_data = [distance,distance2,distance3]
    #history_list.append([car_position[0],car_position[1]]) # add history point
    # moved to within forward/backward to prevent duplicate history points when turning

def fake_sensor():
    travel_time = random.randint(300,350)
    return travel_time
    #decrease movement sleep times for more readings

def change_angle(turn_angle):
    global car_angle
    car_angle+=turn_angle
    if car_angle>360:
        car_angle-=360
    if car_angle<0:
        car_angle+=360

######################

def forward(x):
    print("forward")
    time.sleep(x)
    calculate_position(fake_sensor(),fake_sensor(),fake_sensor(),'forward')

def reverse(x):
    print("reverse")
    time.sleep(x)
    calculate_position(fake_sensor(),fake_sensor(),fake_sensor(),'backward')

def left(x):
    print("left")
    change_angle(turn_angle)
    global car_surface
    car_surface = rot_center(pygame.image.load('car_body.jpg'), car_angle) 
    #redefining a new surface every time as a new image removes artifacting when rotating
    time.sleep(x)
    calculate_position(fake_sensor(),fake_sensor(),fake_sensor(),'left')

def right(x):
    print("right")
    change_angle(-turn_angle)
    global car_surface
    car_surface = rot_center(pygame.image.load('car_body.jpg'), car_angle)
    time.sleep(x)
    calculate_position(fake_sensor(),fake_sensor(),fake_sensor(),'right')

while not gameExit:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
    
    gameDisplay.fill(black)
    #car_body = [screen_width/2-car_width/2,screen_height/2-car_height/2,car_width,car_height]
    #car_front = [screen_width/2-car_width/2,screen_height/2-car_height/2,car_width,10]
    #gameDisplay.fill(red, car_body)
    #gameDisplay.fill(green, car_front)
    
    #detecting key presses and calling motors
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]:
       forward(.5)
    if pressed[pygame.K_a]:
       left(.5)
    if pressed[pygame.K_s]:
       reverse(.5)
    if pressed[pygame.K_d]:
       right(.5)

    gameDisplay.blit(start_surface,[history_list[0][0]-10,history_list[0][1]-10,20,20]) # displaying start point 
    gameDisplay.blit(car_surface,[screen_width/2-car_width/2,screen_height/2-car_height/2,car_width,car_height]) # displaying car
    gameDisplay.blit(arrow_surface,[0,800,0,0])
    #drawing the dots

    for item in sensor_list:
        gameDisplay.fill(white, rect=[item[0],item[1],5,5]) #Dots are size 5x5
    for item in history_list:
        gameDisplay.fill(green, rect=[item[0],item[1],5,5])

    textsurface = myfont.render(str(sensor_data[1]), True, (0, 255, 255)) # left reading
    gameDisplay.blit(textsurface,(0,0))
    textsurface = myfont.render(str(sensor_data[0]), True, (0, 255, 255)) # center reading
    gameDisplay.blit(textsurface,(70,0))
    textsurface = myfont.render(str(sensor_data[2]), True, (0, 255, 255)) # right reading
    gameDisplay.blit(textsurface,(140,0))
    
    gameDisplay.blit(scale_surface,[880,0])

    pygame.display.update()

pygame.quit()
quit()


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

sensor_list = [] #holds all point Objects of type list[x,y]

gameDisplay = pygame.display.set_mode((screen_height,screen_width))
car_surface = pygame.image.load('car_body.jpg')

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

#car_surface = rot_center(car_surface, car_angle) #initial rotation on first load of car sprite

def calculate_position(distance, direction): # calculate sensed object position relative to car, 2 scenarios with 4 quadrants each = 8 conditions
	if direction == "forward":
		movement = calculate_xy_shift(travel_distance, car_angle) #returns how far all dots should move relative to car
		#print(movement)
		#print(car_angle)
		for item in sensor_list:

			item[0]-=movement[0]
			item[1]+=movement[1]

	if direction == "backward":
		movement = calculate_xy_shift(travel_distance, car_angle) #returns how far all dots should move relative to car
		#print(movement)
		#print(car_angle)
		for item in sensor_list:

			item[0]+=movement[0]
			item[1]-=movement[1]

	new_point = calculate_xy_position(distance, car_angle) #position of a new point
	sensor_list.append([car_position[0]+new_point[0],car_position[1]-new_point[1]])

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
	calculate_position(fake_sensor(),'forward')

def reverse(x):
	print("reverse")
	time.sleep(x)
	calculate_position(fake_sensor(),'backward')

def left(x):
	print("left")
	change_angle(turn_angle)
	global car_surface
	car_surface = rot_center(car_surface, turn_angle)
	time.sleep(x)
	calculate_position(fake_sensor(),'left')

def right(x):
	print("right")
	change_angle(-turn_angle)
	global car_surface
	car_surface = rot_center(car_surface, -1*turn_angle)
	time.sleep(x)
	calculate_position(fake_sensor(),'right')

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

	gameDisplay.blit(car_surface,[screen_width/2-car_width/2,screen_height/2-car_height/2,car_width,car_height])

	#drawing the dots
	for item in sensor_list:
		gameDisplay.fill(white, rect=[item[0],item[1],3,3]) #Dots are size 3x3

	pygame.display.update()

pygame.quit()
quit()


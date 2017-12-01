# Author: Yujie Hou
# Last Edit: 11/30/2017

import sys, time, math

def calculate_xy_position(distance, angle):
	shift_x = 0
	shift_y = 0

	shift_x = int(distance*math.cos(math.radians(angle)))
	shift_y = int(distance*math.sin(math.radians(angle)))

	return [shift_x,shift_y]

def calculate_xy_shift(distance, angle):
	shift_x = 0
	shift_y = 0

	shift_x = int(distance*math.cos(math.radians(angle)))
	shift_y = int(distance*math.sin(math.radians(angle)))

	return [shift_x,shift_y]

#print(math.sin(math.radians(90)))
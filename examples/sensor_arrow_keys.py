# This library requires PyAutoGUI - https://pypi.org/project/PyAutoGUI/

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio as aio
from WeDo2 import *
import pyautogui

''' 
Using two WeDos to make an RC car.

One WeDo acts as a steering device, using a Tilt Sensor and a Distance Sensor for input

The other WeDo is the car itself and moves the motors
'''

# Queues to stores updates from the tilt and distance sensors, respectively
tilt_q = aio.Queue()
dist_q = aio.Queue()

# The direction and magnitude we will use to set the motors' speeds
direction = -1
magnitude = 0

screenw, screenh = pyautogui.size()


# Handle tilt sensor updates
def tilt_callback(hub, port, num):
	print(f"TILT: {num}")

	if num == TILT_SENSOR_DIRECTION_NEUTRAL:
		pass
	elif num == TILT_SENSOR_DIRECTION_FORWARD:
		pyautogui.press('up')
	elif num == TILT_SENSOR_DIRECTION_BACKWARD:
		pyautogui.press('down')
	elif num == TILT_SENSOR_DIRECTION_RIGHT:
		pyautogui.press('right')
	elif num == TILT_SENSOR_DIRECTION_LEFT:
		pyautogui.press('left')

# Handle distance sensor updates
def dist_callback(hub, port, num):
	print(f"DIST: {num}")
	magnitude = num

# The main function, where all the meat of the program is
async def main ():
	global tilt_q, dist_q, direction, magnitude

	h = HubManager(1)

	# Connect the WeDos using their MAC addresses
	await h.connect_all()

	# First WeDo has all the sensors
	controller = h.wedos[0]


	# Attach Tilt and Distance Sensors to the controller
	tilt = await controller.attach(1, TiltSensor())
	dist = await controller.attach(2, DistanceSensor())

	# Tilt mode reports predefined movement states
	await tilt.set_mode(TILT_TILT_MODE)
	# Detect mode reports distsance to nearest object, from 1-10
	await dist.set_mode(DIST_DETECT_MODE)

	await controller.set_sensor_callback(1, tilt_callback)
	await controller.set_sensor_callback(2, dist_callback)


	await h.end(True)

loop.run_until_complete(main())
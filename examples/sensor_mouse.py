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
	tilt_q.put_nowait(num)

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


	while True:
		# Every loop check if the quit key has been press (q-Enter)
		await h.end(False)

		try:
			# If there is a new distance update, use it to change the magnitude value
			magnitude = dist_q.get_nowait()
		except aio.QueueEmpty:
			pass

		try:
			# If there is a tilt update, change the direction value
			direction = tilt_q.get_nowait()
		except aio.QueueEmpty:
			pass

		print(magnitude, direction)

		
		currentMouseX, currentMouseY = pyautogui.position()
		
		if direction == TILT_SENSOR_DIRECTION_NEUTRAL:
			pass
		elif direction == TILT_SENSOR_DIRECTION_BACKWARD and currentMouseY+80 < screenh*.7:
			pyautogui.moveTo(currentMouseX, currentMouseY+80, duration=0.01)
		elif direction == TILT_SENSOR_DIRECTION_FORWARD and currentMouseY-80 > screenh*.3:
			pyautogui.moveTo(currentMouseX, currentMouseY-80, duration=0.01)
		elif direction == TILT_SENSOR_DIRECTION_RIGHT and currentMouseX+80 < screenw*.6:
			pyautogui.moveTo(currentMouseX+80, currentMouseY, duration=0.01)
		elif direction == TILT_SENSOR_DIRECTION_LEFT and currentMouseX-80 > screenw*.4:
			pyautogui.moveTo(currentMouseX-80, currentMouseY, duration=0.01)

		if magnitude <= 1:
			pyautogui.click()

		# Allow some buffer time
		await aio.sleep(0)

loop.run_until_complete(main())
# Import WeDo2.py from the parent directory
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WeDo2 import *
import asyncio as aio

# We assume the tilt sensor is plugged into port 1
TILT_PORT_NUM = 1

# Queues to store updates from the distance sensor
tilt_q = aio.Queue()

""" 
This function is called when the tilt sensor updates
The library calls this function, and gives it the following arguments:
	hub - the WeDo that the tilt sensor is connected to
	port - the port the tilt sensor is on
	num - the value the tilt sensor got

"""
def tilt_callback(hub, port, num):
	tilt_q.put_nowait(num)

""" The main loop for the program """
async def main ():
	global tilt_q

	# Hub managers store all the WeDos you wish to connect
	h = HubManager(1)

	# Search and establish connections w/ WeDos
	await h.connect_all()

	wedo = h.wedos[0]

	# Register the tilt sensor in the specified port (TILT_PORT_NUM=1, in this case)
	t_sensor = await wedo.attach(TILT_PORT_NUM, TiltSensor())

	# Tilt sensors in tilt mode report one of several predefined tilt states (forward, backward, etc.)
	await t_sensor.set_mode(TILT_TILT_MODE)

	# When the sensor on port 1 (TILT_PORT_NUM=1) receives an update, call dist_callback
	await wedo.set_sensor_callback(TILT_PORT_NUM, tilt_callback)

	while True:
		# Every loop check if the quit key has been press (q-Enter)
		await h.end(False)

		try:
			# If there is a new tilt update, get it from the queue
			# then based on the direction of its tilt, print something
			# If you wanted to, you could just print in the callback, but I wanted to show how you could interact
			# between the main loop (async) and the callback (synchronous)
			t = tilt_q.get_nowait()

			direction = 'UNKNOWN'

			if t == TILT_SENSOR_DIRECTION_NEUTRAL:
				direction = 'NEUTRAL'
			elif t == TILT_SENSOR_DIRECTION_BACKWARD:
				direction = 'BACKWARD'
			elif t == TILT_SENSOR_DIRECTION_RIGHT:
				direction = 'RIGHT'
			elif t == TILT_SENSOR_DIRECTION_LEFT:
				direction = 'LEFT'
			elif t == TILT_SENSOR_DIRECTION_FORWARD:
				direction = 'FORWARD'

			print(t, direction)

		except aio.QueueEmpty:
			pass


		# Allow some buffer time between each loop
		await aio.sleep(0)

# loop from the WeDo2 library, run the main function
loop.run_until_complete(main())
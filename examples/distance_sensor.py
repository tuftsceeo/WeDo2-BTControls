# Import WeDo2.py from the parent directory
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WeDo2 import *
import asyncio as aio

# Queues to store updates from the distance sensor
dist_q = aio.Queue()

""" 
This function is called when the distance sensor updates
	hub - the distance sensor's hub
	port - the port the distance sensor is on
	num - the value it reported

"""
def dist_callback (hub, port, num):
	dist_q.put_nowait(num)


""" The main loop for the program """
async def main ():
	global dist_q

	# Hub managers store all the WeDos you wish to connect
	h = HubManager(1)

	# Search and establish connections w/ WeDos
	await h.connect_all()

	wedo = h.wedos[0]

	# Register the distance sensor in port 1
	d_sensor = await wedo.attach(1, DistanceSensor())

	# Detect mode reports distsance to nearest object, from 1-10
	await d_sensor.set_mode(DIST_DETECT_MODE)

	# When the sensor on port 1 receives an update, call dist_callback
	await controller.set_sensor_callback(1, dist_callback)

	while True:
		# Every loop check if the quit key has been press (q-Enter)
		await h.end(False)

		try:
			# If there is a new distance update, get it from the queue and print it
			# If you wanted to, you could just print it in the callback, but I wanted to show how you could interact
			# between the main loop (async) and the callback (synchronous)
			d = dist_q.get_nowait()

			print(f'Got an update: {d}!')
		except aio.QueueEmpty:
			pass


		# Allow some buffer time between each loop
		await aio.sleep(0)

# loop from the WeDo2 library, run the main function
loop.run_until_complete(main())
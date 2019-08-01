# Import WeDo2.py from the parent directory
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WeDo2 import *
import asyncio as aio

# Queues to store updates from the distance sensor
dist_q = aio.Queue()

motor_speed = 0

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
	global dist_q, motor_speed

	"""
	The WeDo setup:
	- 1 WeDo with only a distance sensor attached on port 1 (brain, have it connect first)
	- 1 WeDo with two motors attached (driver)
	"""
	h = HubManager(2)

	# Search and establish connections w/ WeDos
	await h.connect_all()

	brain = h.wedos[0]
	driver = h.wedos[1]

	# Register the distance sensor in port 1 of the brain
	d_sensor = await brain.attach(1, DistanceSensor())

	# Register motors
	m1 = await driver.attach(1, Motor())
	m2 = await driver.attach(2, Motor())

	# Detect mode reports distsance to nearest object, from 1-10
	await d_sensor.set_mode(DIST_DETECT_MODE)

	# When the sensor on port 1 receives an update, call dist_callback
	await brain.set_sensor_callback(1, dist_callback)

	while True:
		# Every loop check if the quit key has been press (q-Enter)
		await h.end(False)

		try:
			# distance sensor will set a motor speed; distance sensor reports 1-10, set_speed takes 0 to 1
			motor_speed = dist_q.get_nowait()/10

			print(f'Got an update: {motor_speed}!')
		except aio.QueueEmpty:
			pass


		# Set motors' speeds
		m1.set_speed(motor_speed)
		m2.set_speed(motor_speed)


		# Allow some buffer time between each loop
		await aio.sleep(0)

# loop from the WeDo2 library, run the main function
loop.run_until_complete(main())
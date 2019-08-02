import os, sys, math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio as aio
from WeDo2 import *

''' 
Using two WeDos to make an RC car.

One WeDo acts as a steering device, using a Tilt Sensor and a Distance Sensor for input

The other WeDo is the car itself and moves the motors
'''

# Queues to stores updates from the tilt and distance sensors, respectively
pitch_q = aio.Queue()
roll_q = aio.Queue()

# The direction and magnitude we will use to set the motors' speeds

# Handle tilt sensor updates
def tilt_callback(hub, port, num):
	print(f"TILT {port}: {num}")

	if port == 1:
		pitch_q.put_nowait(num)
	else:
		roll_q.put_nowait(num)		

# The main function, where all the meat of the program is
async def main ():
	global tilt_q, dist_q, direction, magnitude

	h = HubManager(2)

	# Connect the WeDos using their MAC addresses
	await h.connect_all()

	# First WeDo has all the sensors
	controller = h.wedos[0]
	# Second WeDo controls the motors
	car = h.wedos[1]

	# Attach Tilt and Distance Sensors to the controller
	pitch = await controller.attach(1, TiltSensor())
	roll = await controller.attach(2, TiltSensor())

	# Attach motors to the motor car
	m1 = await car.attach(1, Motor())
	m2 = await car.attach(2, Motor())

	# Tilt mode reports predefined movement states
	await pitch.set_mode(TILT_ANGLE_MODE)
	await roll.set_mode(TILT_ANGLE_MODE)

	await controller.set_sensor_callback(1, tilt_callback)
	await controller.set_sensor_callback(2, tilt_callback)


	while True:
		# Every loop check if the quit key has been press (q-Enter)
		await h.end(False)

		try:
			# If there is a new distance update, use it to change the magnitude value
			p = pitch_q.get_nowait()
			r = roll_q.get_nowait()
		except aio.QueueEmpty:
			pass

		try:
			# If there is a tilt update, change the direction value
			direction = tilt_q.get_nowait()
		except aio.QueueEmpty:
			pass

		print(magnitude, direction)

        
		normalized_pitch = (((p+45)%256)-45)/45
		normalized_roll = (((r+45)%256)-45)/45

                await m1.set_speed(normalized_pitch)
                await m2.set_speed(normalized_pitch,.8915)

		# Allow some buffer time
		await aio.sleep(0)

loop.run_until_complete(main())

import sys
import asyncio as aio
from WeDo2 import *

''' 
Using two WeDos to make an RC car.

One WeDo acts as a steering device, using an OpenMV camera that detects QR Codes (qrcodes/demo/) for input

The other WeDo is the car itself and moves the motors
'''

# Queues to stores updates from the camera
openmv_q = aio.Queue()

# The direction we will use to set the motors' speeds
direction = 0

# Numbers that the OpenMV sends based on the qr code
STOP = 0
FORWARD = 10
BACKWARD = 20
LEFT = 30
RIGHT = 40

# Handle distance sensor updates
def openmv_callback(hub, port, num):
	print(f"CAMERA: {num}")
	openmv_q.put_nowait(num)

# The main function, where all the meat of the program is
async def main ():
	global openmv_q, direction

	h = HubManager(2)

	# Connect the WeDos using their MAC addresses
	await h.connect_all(['A0:E6:F8:1B:61:FC', '0C:61:CF:C9:B0:39'])

	# First WeDo has all the sensors
	controller = h.wedos[0]
	# Second WeDo controls the motors
	car = h.wedos[1]

	# Attach OpenMV to the controller (detects it as a distance sensor)
	cam = await controller.attach(1, DistanceSensor())

	# Attach motors to the motor car
	m1 = await car.attach(1, Motor())
	m2 = await car.attach(2, Motor())

	# Detect mode reports distsance to nearest object, from 1-10
	await cam.set_mode(DIST_DETECT_MODE)

	await controller.set_sensor_callback(1, openmv_callback)

	while True:
		# Every loop check if the quit key has been press (q-Enter)
		await h.end(False)

		try:
			# If there is a new distance update, use it to change the magnitude value
			n = openmv_q.get_nowait()
			# assign magnitude and direction based on number sent
			direction = n
		except aio.QueueEmpty:
			pass

		print(direction)

		# Depending on the direction, change the motor speeds.
		# TODO: 8-way direction and document "motor factoring" and turn factoring
		if direction == STOP:
			await m1.set_speed(0)
			await m2.set_speed(0)
		elif direction == FORWARD:
			await m1.set_speed(1)
			await m2.set_speed(-1,.8915)
		elif direction == BACKWARD:
			await m1.set_speed(-1)
			await m2.set_speed(1,.8915)
		elif direction == RIGHT:
			await m1.set_speed(1*.5)
			await m2.set_speed(1*.5,.8915)
		elif direction == LEFT:
			await m1.set_speed(-1*.5)
			await m2.set_speed(-1*.5,.8915)

		# Allow some buffer time
		await aio.sleep(0)

loop.run_until_complete(main())
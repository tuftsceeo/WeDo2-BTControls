import sys
import asyncio as aio
from WeDo2 import *

tilt_q = aio.Queue()
dist_q = aio.Queue()

direction = -1
magnitude = 0

async def quit():
	res = await loop.run_in_executor(None, sys.stdin.readline)
	if res.strip() == 'q':
		quit_q.put_nowait('q')

def tilt_callback(hub, port, num):
	print(f"TILT: {num}")
	tilt_q.put_nowait(num)

def dist_callback(hub, port, num):
	print(f"DIST: {num}")
	dist_q.put_nowait(num)

async def main ():
	global tilt_q, dist_q, direction, magnitude

	h = HubManager(2)

	await h.connect_all(['A0:E6:F8:1B:61:FC', '0C:61:CF:C9:B0:39'])

	brain = h.wedos[0]
	controller = h.wedos[1]

	tilt = await brain.attach(1, TiltSensor())
	dist = await brain.attach(2, DistanceSensor())

	m1 = await controller.attach(1, Motor())
	m2 = await controller.attach(2, Motor())

	await tilt.set_mode(TILT_TILT_MODE)
	await dist.set_mode(DIST_DETECT_MODE)

	await brain.set_sensor_callback(1, tilt_callback)
	await brain.set_sensor_callback(2, dist_callback)


	while True:
		await h.end(False)

		try:
			n = dist_q.get_nowait()
			magnitude = 1 - n/10
		except aio.QueueEmpty:
			pass

		try:
			direction = tilt_q.get_nowait()
		except aio.QueueEmpty:
			pass

		print(magnitude, direction)

		if direction == TILT_SENSOR_DIRECTION_NEUTRAL:
			await m1.set_speed(0)
			await m2.set_speed(0)
		elif direction == TILT_SENSOR_DIRECTION_FORWARD:
			await m1.set_speed(magnitude)
			await m2.set_speed(-magnitude)
		elif direction == TILT_SENSOR_DIRECTION_BACKWARD:
			await m1.set_speed(-magnitude)
			await m2.set_speed(magnitude)
		elif direction == TILT_SENSOR_DIRECTION_RIGHT:
			await m1.set_speed(magnitude*.5)
			await m2.set_speed(magnitude*.5)
		elif direction == TILT_SENSOR_DIRECTION_LEFT:
			await m1.set_speed(-magnitude*.5)
			await m2.set_speed(-magnitude*.5)

		await aio.sleep(0)

	# await h.end()

loop.run_until_complete(main())
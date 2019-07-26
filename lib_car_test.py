import sys, math
import asyncio as aio
from WeDo2 import *

memory = []
dHeightIN = 9/2.54

dist_q = aio.Queue()

quit_q = aio.LifoQueue()
dist_threshold = 12

scale_factor = 80/math.tan(27.8*math.pi/180)

def callback(hub, port, num):
	dist_q.put_nowait( (port, num) )

async def quit():
	res = await loop.run_in_executor(None, sys.stdin.readline)
	if res.strip() == 'q':
		quit_q.put_nowait('q')

async def main():

	global dist_q, dist_threshold, quit_q, scale_factor

	aio.create_task(quit())

	h = HubManager(2)

	await h.connect_all(['24:71:89:17:9D:AE', '24:71:89:09:CB:21'])

	wedo = h.wedos[0]
	wedo2 = h.wedos[1]

	await wedo.attach(1, DistanceSensor()) # bottom
	await wedo.attach(2, DistanceSensor()) # top

	await wedo2.attach(1, Motor())
	await wedo2.attach(2, Motor()) 


	await wedo.ports[0].set_mode(DIST_DETECT_MODE)
	await wedo.ports[1].set_mode(DIST_DETECT_MODE)

	await wedo.set_sensor_callback(2, callback)
	await wedo.set_sensor_callback(1, callback)	


	# await quit_q.get()

	select = (1,0)

	while True:
		try:
			q = quit_q.get_nowait()
			print('quitting...')
			break
		except aio.QueueEmpty:
			print()


		port, num = await dist_q.get()

		if port == select[0]:
			select = (port, num)
			continue

		bot = 255
		top = 255

		if port == 1:
			bot = num
			top = select[1]
		else:
			bot = select[1]
			top = num

		print (bot, top)

		if not ( top == 255 or bot == 255 or bot > top or top == bot):
			difference = top - bot
			distanceIN = (dHeightIN/difference)*scale_factor
			#distanceIN = distanceCM/2.54

			dist = distanceIN

			print(f"{dist} inches away")

			if dist < dist_threshold:

				await wedo2.ports[0].set_speed(0)
				await wedo2.ports[1].set_speed(0)

				# data = bytearray([0x01, 0x01, 0x01, 0 ])
				# await wedo2.client.write_gatt_char(OUTPUT_COMMAND_UUID, data, True )

				await wedo2.set_led_color(LED_INDEX_PINK)
			else:

				await wedo2.ports[0].set_speed(1)
				await wedo2.ports[1].set_speed(-1)

				# data = bytearray([0x01, 0x01, 0x01, 0x9C ])
				# await wedo2.client.write_gatt_char(OUTPUT_COMMAND_UUID, data, True )
				await wedo2.set_led_color(3)



	await h.disconnect_all()		

loop.run_until_complete(main())
loop.close()
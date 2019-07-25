import asyncio as aio
from WeDo2 import *

test = aio.Queue()

def callback(hub, port, num):
	if num<5:
		test.put_nowait(hub)

async def run():
	h = HubManager(1)

	await h.connect_all()
	print(len(h.wedos))

	await h.wedos[0].attach(1, Motor())
	await h.wedos[0].attach(2, DistanceSensor())

	await h.wedos[0].ports[1].set_mode(DIST_DETECT_MODE)

	await h.wedos[0].set_sensor_callback(2, callback)

	# await h.wedos[0].ports[0].set_speed(1)

	await aio.sleep(1)
	
	# await h.wedos[0].ports[0].set_speed(0)
	
	# await h.wedos[0].set_led_color(LED_INDEX_PURPLE)	

	ready = await test.get()
	await ready.set_led_color(LED_INDEX_PINK)



	await aio.sleep(10)

	await h.disconnect_all()


loop.run_until_complete(run())
loop.close()
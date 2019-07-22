from WeDo2 import *
from bleak import BleakClient
import asyncio

# h = HubManager(1)

# h.wedos[0].set_led_mode(LED_DISCREET_MODE)
# h.wedos[0].set_led_color(255,0,0)

async def run():
	await BleakClient(address='24:71:89:17:9D:AE', loop=loop).connect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
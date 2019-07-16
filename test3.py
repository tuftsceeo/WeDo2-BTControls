import asyncio
from bleak import BleakClient
import time

address = "24:71:89:17:9D:AE"

PORT_NUM = 0x01

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
PORT_INFO_UUID = '00001527-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'

print('Connecting to the WeDo 2.0')

def callback (sender, data):
	int_values = [x for x in data]

	print(f"{sender}: {int_values} / {data}")

async def run(address, loop):
	async with BleakClient(address, loop=loop) as client:
		print ('Connected successfully!')

		await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]) )

		await client.start_notify(SENSOR_VAL_UUID, callback)

		try:
			while True:	
				await asyncio.sleep(5.0, loop=loop)
		except KeyboardInterrupt:
			print('Stopping notifications...')
			await client.stop_notify(SENSOR_VAL_UUID)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
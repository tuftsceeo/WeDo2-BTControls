import asyncio
from bleak import BleakClient
import time

address = "24:71:89:17:9D:AE"

PORT_NUM = 0x02

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
PORT_INFO_UUID = '00001527-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'
OUTPUT_COMMAND_UUID = '00001565-1212-efde-1523-785feabcd123'


print('Connecting to the WeDo 2.0')

def callback (sender, data):
	print('notified!')

	print(f"{sender}: {data}")

async def run(address, loop):
	async with BleakClient(address, loop=loop) as client:
		print ('Connected successfully!')

		await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)

		await client.start_notify(SENSOR_VAL_UUID, callback)

		# global outputted_value
		
		try:
			while True:	
				# print(await client.read_gatt_char(PORT_INFO_UUID))
				await asyncio.sleep(1)
				# print(outputted_value)
				# await client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x03,outputted_value[0], outputted_value[1], outputted_value[2]]), True)

		except KeyboardInterrupt:
			print('Stopping notifications...')
			await client.stop_notify(SENSOR_VAL_UUID)


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
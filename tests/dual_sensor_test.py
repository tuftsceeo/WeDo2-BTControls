import sys
import uuid
import asyncio
from bleak import BleakClient

address = '24:71:89:17:9D:AE'

client = None

OPENMV_PORT_NUM = 0x01
DIST_PORT_NUM = 0x02

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'

PORT_NOTIF_UUID = '00001524-1212-efde-1523-785feabcd123'


loop = asyncio.get_event_loop()

def sensor_callback(sender, data):
	print(f"{sender}: {data}")

	def _():
		pass

async def run (mac, loop):
	client = BleakClient(mac, loop=loop)

	await client.connect()

	await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,OPENMV_PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)
	await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,DIST_PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)

	await client.write_gatt_char(PORT_NOTIF_UUID, [0x00, 0x41, OPENMV_PORT_NUM, 0x00, 1, 0, 0, 0, 1])
	await client.write_gatt_char(PORT_NOTIF_UUID, [0x00, 0x41, DIST_PORT_NUM, 0x00, 1, 0, 0, 0, 1])

	await client.start_notify(SENSOR_VAL_UUID, sensor_callback)
	# await client.start_notify('00002803-0000-1000-8000-00805f9b34fb')


	while True:
		res = await loop.run_in_executor(None, sys.stdin.readline)
			
		print(res)

		if res.strip() == 'q':
			print('quitting...')
			break

		await asyncio.sleep(0.5)

	await client.stop_notify(SENSOR_VAL_UUID)
	await client.disconnect()


# loop.add_reader(sys.stdin.fileno(), input_handle)

# loop.run_until_complete(aio_readline(loop))
loop.run_until_complete( run(address, loop) )

loop.close()
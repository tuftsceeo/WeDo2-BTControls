import asyncio
from bleak import BleakClient
import time

address = "24:71:89:17:9D:AE"

PORT_NUM = 0x01

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
PORT_INFO_UUID = '00001527-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'
OUTPUT_COMMAND_UUID = '00001565-1212-efde-1523-785feabcd123'

outputted_value = 1;

print('Connecting to the WeDo 2.0')

def callback (sender, data):
	int_values = [x for x in data]
	y = int_values[-1]
	x= int_values[-2]
	print(f"{sender}: {int_values} / {data} : {y} : {x}")
	global outputted_value
	outputted_value = convertToNumber(x,y)

def convertToNumber(x, y):
	if x == 0 and y == 0:
		return 0
	if x == 0 and y == 195:
		return 128
	
	offset = (4**(y%128 - 63))/(2 if x < 128 else 1) * (1 + (x%128/128))
	number = offset if y < 128 else 256-offset
	return int(number)

def translate_speed(speed):
    if speed < 0:
        return int((0x54*max(speed,-1))+0xF0)
    elif speed > 0:
        return int((0x54*min(speed,1))+0x10)
    else:
        return 0x00

async def run(address, loop):
	async with BleakClient(address, loop=loop) as client:
		print ('Connected successfully!')

		await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)

		await client.start_notify(SENSOR_VAL_UUID, callback)

		# global outputted_value
		
		try:
			while True:	
				asyncio.sleep(1)
				# await client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01,outputted_value]), True)
				# print(await client.read_gatt_char(PORT_INFO_UUID))
				# await client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x02, 0x01, 0x01, translate_speed(outputted_value/10)]))

		except KeyboardInterrupt:
			print('Stopping notifications...')
			await client.stop_notify(SENSOR_VAL_UUID)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))

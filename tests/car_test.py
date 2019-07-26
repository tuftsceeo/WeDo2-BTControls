import sys
import uuid
import asyncio
from bleak import BleakClient

address1 = '24:71:89:17:9D:AE'
address2 = '24:71:89:09:CB:21'

client = None

OPENMV_PORT_NUM = 0x01
DIST_PORT_NUM = 0x01

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'
OUTPUT_COMMAND_UUID = '00001565-1212-efde-1523-785feabcd123'

PORT_NOTIF_UUID = '00001524-1212-efde-1523-785feabcd123'

outputted_value_1 = 10
prev_outputted_value_1 = 10

outputted_value_2 = 0
prev_outputted_value_2 = 0

Q = []

loop = asyncio.get_event_loop()

def sensor_callback(sender, data):
	global outputted_value_1, outputted_value_2

	int_values = [a for a in data]
	x,y = int_values[-2:]

	port = int_values[1]

	num = convertToNumber(x,y)

	print(f"{port}: {num}")

	outputted_value_1 = num
	outputted_value_2 = num

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

async def run (mac1, mac2, loop):
	client = BleakClient(mac1, loop=loop)
	client2 = BleakClient(mac2, loop=loop)

	await client.connect()
	await client2.connect()

	# await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,OPENMV_PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)
	await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,DIST_PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)

	# await client.write_gatt_char(PORT_NOTIF_UUID, [0x00, 0x41, OPENMV_PORT_NUM, 0x00, 1, 0, 0, 0, 1])
	await client.write_gatt_char(PORT_NOTIF_UUID, [0x00, 0x41, DIST_PORT_NUM, 0x08, 1, 0, 0, 0, 1])

	await client.start_notify(SENSOR_VAL_UUID, sensor_callback)
	# await client.start_notify('00002803-0000-1000-8000-00805f9b34fb')




	global Q, outputted_value_1, outputted_value_2, prev_outputted_value_1, prev_outputted_value_2

	while True:
		# res = await loop.run_in_executor(None, sys.stdin.readline)
			
		# print(outputted_value_1)

		# if res.strip() == 'q':
		# 	print('quitting...')
		# 	break

		# if outputted_value_1 == prev_outputted_value_1 and outputted_value_2 == prev_outputted_value_2:
		# 	continue
		copy = outputted_value_1

		await client2.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01,copy]), True  )
		await client2.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x01, 0x01, 0x01, translate_speed(  (.8 if copy>9 else -.8	)  ) ]), True )
		await client2.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x02, 0x01, 0x01, translate_speed(  (-.8	)  ) ]), True )

		prev_outputted_value_1 = outputted_value_1
		prev_outputted_value_2 = outputted_value_2

		# await asyncio.sleep(0.5)

	await client.stop_notify(SENSOR_VAL_UUID)
	await client.disconnect()
	await client2.disconnect()


# loop.add_reader(sys.stdin.fileno(), input_handle)

# loop.run_until_complete(aio_readline(loop))
loop.run_until_complete( run(address1, address2, loop) )

loop.close()
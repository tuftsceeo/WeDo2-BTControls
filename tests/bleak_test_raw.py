import asyncio
from bleak import BleakClient
import time

address1 = "24:71:89:17:9D:AE"
address2 = "24:71:89:09:CB:21"

PORT_NUM = 0x02

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
PORT_INFO_UUID = '00001527-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'
OUTPUT_COMMAND_UUID = '00001565-1212-efde-1523-785feabcd123'

GLOBAL_Q = []

outputted_value = 1

prev_value = outputted_value

print('Connecting to two WeDo 2.0\'s...')

loop = asyncio.get_event_loop()

def process_q ():
	global GLOBAL_Q
	for q in GLOBAL_Q:
		try:
			# Write
			hub, uuid, data = q

			async def _():
				await hub.client.write_gatt_char(uuid, data, True)

			loop.run_until_complete(_())
		except ValueError:
			# Read
			hub, uuid = q
			hub.client.read_gatt_char(uuid)

	GLOBAL_Q = []

def callback (sender, data):
	int_values = [x for x in data]
	print('notified!')
	y = int_values[-1]
	x= int_values[-2]
	
	global outputted_value
	
	outputted_value = convertToNumber(x,y)	

	print(f"{sender}: {int_values} / {outputted_value}")

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

async def run(addr1, add2, loop):
	async with BleakClient(addr1, loop=loop) as client:
		print('Connected to the first WeDo successfully!')

		async with BleakClient(add2, loop=loop) as client2:
			print ('Connected to the second WeDo successfully!')
			
			await client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)

			await client.start_notify(SENSOR_VAL_UUID, callback)


			# await client2.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]), True)

			# await client2.start_notify(SENSOR_VAL_UUID, callback)

			global outputted_value, prev_value, GLOBAL_Q
			
			try:
				while True:	
					await asyncio.sleep(0)

					if not outputted_value == prev_value:

						copy = outputted_value

						GLOBAL_Q.append( (client, OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01,copy]) ) )
						GLOBAL_Q.append( (client2, OUTPUT_COMMAND_UUID, bytearray([0x01, 0x01, 0x01, translate_speed(  copy>0  ) ]) ) )
						GLOBAL_Q.append( (client2, OUTPUT_COMMAND_UUID, bytearray([0x02, 0x01, 0x01, translate_speed(  (copy>0) * (-1 if copy<4 else 1) ) ]) ) )


						for q in GLOBAL_Q:
							try:
								# Write
								c, uuid, data = q
								await c.write_gatt_char(uuid, data, True)

							except ValueError:
								# Read
								c, uuid = q
								c.read_gatt_char(uuid)

						GLOBAL_Q = []

						# await client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01,copy]), True)
						
						# await client2.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01,copy]), True)
						# await client2.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x01, 0x01, 0x01, translate_speed(copy/10) ]), True )
						# await client2.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x02, 0x01, 0x021, translate_speed(-copy/10) ]), True )


					prev_value = outputted_value

					# await client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01,outputted_value]), True)
					# print(await client.read_gatt_char(PORT_INFO_UUID))
					# await client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x02, 0x01, 0x01, translate_speed(outputted_value/10)]))

			except KeyboardInterrupt:
				print('Stopping notifications...')
				await client.stop_notify(SENSOR_VAL_UUID)
				# await client2.stop_notify(SENSOR_VAL_UUID)

loop.run_until_complete(run(address1, address2, loop))

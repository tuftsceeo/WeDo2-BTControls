from pygatt import *
import time

adapter = GATTToolBackend()

adapter.start()

device = adapter.connect('24:71:89:17:9D:AE')

help(device)

PORT_NUM = 0x01

# print(device.char_read_handle(32))

device.char_write_handle(0x3a, bytearray([0x01,0x02,PORT_NUM,0x23,0x00,0x01,0x00,0x00,0x00,0x02,0x01]))

def thing(e):
	print(e)

# device.receive_notification(32, thing)

while True:
	print('attempt')
	try:
		print(device.char_read_handle(32))
	except Exception as e:
		time.sleep(0.2)
		continue
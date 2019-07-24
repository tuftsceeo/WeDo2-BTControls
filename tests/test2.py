from pygatt import *
import time

adapter = GATTToolBackend()

adapter.start()

device = adapter.connect('24:71:89:09:CB:21')


PORT_NUM = 0x01

# print(device.char_read_handle(32))

device.char_write_handle(0x3d, bytearray([2, 1, 1, 0x64]))
# device.char_write_handle(0x3d, bytearray([2, 1, 1, 0x9C]))

time.sleep(0.5)

device.char_write_handle(0x3d, bytearray([1, 1, 1, 0]))
device.char_write_handle(0x3d, bytearray([2, 1, 1, 0]))
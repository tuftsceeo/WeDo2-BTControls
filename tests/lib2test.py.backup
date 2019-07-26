from WeDo2 import *
from bleak import BleakClient
import asyncio

def translate_speed(speed):
    if speed < 0:
        return int((0x54*max(speed,-1))+0xF0)
    elif speed > 0:
        return int((0x54*min(speed,1))+0x10)
    else:
        return 0x00

h = HubManager(1)

# h.wedos[0].set_led_mode(LED_DISCREET_MODE)

# for i in range(10):
# 	print('INDEX: ' + str(i))	
# 	h.wedos[0].set_led_color(i)
# 	asyncio.sleep(5)


GLOBAL_Q.append( (h.wedos[0], OUTPUT_COMMAND_UUID, bytearray([0x01, 0x01, 0x01, translate_speed(0.5) ])) )
GLOBAL_Q.append( (h.wedos[0], OUTPUT_COMMAND_UUID, bytearray([0x02, 0x01, 0x01, translate_speed(-0.5) ])) )

process_q()



# while True:
# 	asyncio.sleep(1)
# h.wedos[0].set_led_color(255,0,0)

# loop = asyncio.get_event_loop()

# async def run():
# 	await BleakClient(address='24:71:89:17:9D:AE', loop=loop).connect()

# loop.run_until_complete(run())
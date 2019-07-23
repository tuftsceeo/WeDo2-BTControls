import asyncio
from bleak import BleakClient, discover

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
PORT_INFO_UUID = '00001527-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'
OUTPUT_COMMAND_UUID = '00001565-1212-efde-1523-785feabcd123'

LED_ABSOLUTE_MODE = 0
LED_DISCREET_MODE = 1

# LED index colors
LED_INDEX_PINK = 0x01
LED_INDEX_PURPLE = 0x02

loop = asyncio.get_event_loop()

GLOBAL_Q = []

class HubManager():
	"""docstring for HubManager"""
	def __init__(self, wnum):
		self.wedos = []


		for _ in range(wnum):
			loop.run_until_complete( self.get_wedo() )

	async def get_wedo(self):
		devices = await discover()
		for d in devices:
			mac_addr = str(d).split(' ',1)[0][:-1]
			name = str(d).split(' ',1)[1]
			

			if mac_addr.startswith('24:71:89:') or 'LPF2 Smart Hub' in name:
				print(d)
				client = BleakClient(mac_addr, loop=loop)
				await client.connect()
				self.wedos.append( Smarthub( client ) )

class Smarthub ():
	def __init__(self, client):
		self.client = client

	def set_led_mode (self, mode):

		async def _():
			await self.client.write_gatt_char(INPUT_COMMAND_UUID, bytearray([0x01,0x02,0x06,0x17,mode,0x01,0x00,0x00,0x00,0x02,0x01]), True)

		loop.run_until_complete(_())

	def set_led_color (self, *args):
		async def _():
			pass


		if len(args) == 1:
			async def _():
				await self.client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01, args[0] ]), True)
					
		elif len(args) == 3:
			r,g,b = args

			async def _():
				await self.client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray( [0x06,0x04,0x03,r,g,b] ), True)

		else:
			raise Exception('Incorrect arguments, either pass 1 (index) number or 3 (rgb)')

		loop.run_until_complete(_())


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
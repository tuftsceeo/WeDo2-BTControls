import sys
import asyncio as aio
from bleak import BleakClient, discover

SENSOR_VAL_UUID = '00001560-1212-efde-1523-785feabcd123'
PORT_INFO_UUID = '00001527-1212-efde-1523-785feabcd123'
INPUT_COMMAND_UUID = '00001563-1212-efde-1523-785feabcd123'
OUTPUT_COMMAND_UUID = '00001565-1212-efde-1523-785feabcd123'
PORT_NOTIF_UUID = '00001524-1212-efde-1523-785feabcd123'

LED_ABSOLUTE_MODE = 0
LED_DISCREET_MODE = 1

# LED index colors
LED_INDEX_PINK = 0x01
LED_INDEX_PURPLE = 0x02

DIST_DETECT_MODE = 0
DIST_COUNT_MODE = 1

TILT_ANGLE_MODE = 0
TILT_TILT_MODE = 1
TILT_CRASH_MODE = 2

TILT_SENSOR_DIRECTION_NEUTRAL  = 0
TILT_SENSOR_DIRECTION_BACKWARD = 3
TILT_SENSOR_DIRECTION_RIGHT    = 5
TILT_SENSOR_DIRECTION_LEFT     = 7
TILT_SENSOR_DIRECTION_FORWARD  = 9
TILT_SENSOR_DIRECTION_UNKNOWN  = 10

loop = aio.get_event_loop()

quit_q = aio.LifoQueue()


""" Listen for a q-ENTER, in which case, put something in the Quit detection Queue """
async def quit():
	res = await loop.run_in_executor(None, sys.stdin.readline)
	if res.strip() == 'q':
		quit_q.put_nowait('q')

""" Convert bytes sent from WeDo sensors into decimal values """
def convertToNumber(x, y):
	if x == 0 and y == 0:
		return 0
	if x == 0 and y == 195:
		return 128
	
	offset = (4**(y%128 - 63))/(2 if x < 128 else 1) * (1 + (x%128/128))
	number = offset if y < 128 else 256-offset
	return int(number)	

class HubManager():
	""" Holds and connects any specified amount of WeDo hubs """
	def __init__(self, wnum):
		self.wnum = wnum
		self.wedos = []
		self.task = None

	""" Connect the number of WeDos specified at instantiation, either by discovering them or using provided MAC addresses """
	async def connect_all (self, addresses=[]):
		self.task = aio.ensure_future(quit())

		print('Connecting...')
		for i in range(self.wnum):
			mac = ''

			try:
				mac = addresses[i]
			except IndexError:
				# No address, find wedo
				mac = await self.find_wedos()

			client = BleakClient(mac, loop=loop)
			await client.connect()

			print(f'Connected to WeDo: {mac}')

			self.wedos.append( Hub(client) )

	""" Disconnect all hubs """
	async def disconnect_all(self):
		print('Disconnecting...')
		for w in self.wedos:
			await w.disconnect()

	""" Find a WeDo and return its MAC address """
	async def find_wedos(self):
		devices = await discover()
		
		for d in devices:
			mac_addr = str(d).split(' ',1)[0][:-1]
			name = str(d).split(' ',1)[1]
			
			if mac_addr.startswith('24:71:89:') or 'LPF2 Smart Hub' in name:
				# Found a WeDo!
				print(f"Found {d}")
				return mac_addr

	""" If the quit key was pressed, start the ending/disconnect process """
	async def end(self, block=True):
		global quit_q

		if block:
			await quit_q.get()
			
			print('Ending...')
			self.task.cancel()

			await self.disconnect_all()
		else:
			try:
				quit_q.get_nowait()
				print('Ending...')
				self.task.cancel()

				await self.disconnect_all()
			except:
				return

class Hub():
	""" Represents the WeDo """
	def __init__(self, client):
		self.client = client
		self.ports = [None]*2
		self.callbacks = [None]*2

	async def disconnect(self):
		await self.client.disconnect()

	""" 
	Set the LED to one of two modes:
		LED_ABSOLUTE_MODE - Change color using LEGO's presets
		LED_DISCREET_MODE - Change color using RGB value

	 """ 
	async def set_led_mode(self, mode):
		await client.write_gatt_char(INPUT_COMMAND_UUID, 
			bytearray([0x01,0x02,0x06,0x17,mode,0x01,0x00,0x00,0x00,0x02,0x01]), True)

	async def set_led_color(self, color):
		try:
			r,g,b = color
			await self.client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray( [0x06,0x04,0x03,r,g,b] ), True)
		except TypeError:
			await self.client.write_gatt_char(OUTPUT_COMMAND_UUID, bytearray([0x06,0x04,0x01, color ]), True)

	""" Connect an Attachment/peripherial (motors, sensors, etc.) to the Hub """	
	async def attach(self, port, periph):
		if isinstance(periph, Attachment):
			periph.client = self.client
			periph.port = port
			self.ports[port-1] = periph

			return periph
		else:
			raise Exception('AHH! You can only attach and Attachment!! >:(')

	""" Set a callback to for a sensor at some port. Whenever the sensor updates, the callback will be called"""
	async def set_sensor_callback(self, port, cb):
		# Set port notifications
		await self.client.write_gatt_char(PORT_NOTIF_UUID, [0x00, 0x41, port, 0x08, 1, 0, 0, 0, 1])

		def sensor_cleaner(sender, data):
			# print(data)

			int_values = [a for a in data]
			
			s_port = int_values[1]

			if port==6:
				return

			x,y = int_values[-2:]
			num = convertToNumber(x,y)

			# print(f'got it: {num}')
			# print(self.callbacks)
			try:
				self.callbacks[s_port-1](self, s_port, num)
			except Exception:
				pass

		self.callbacks[port-1] = cb

		await self.client.start_notify(SENSOR_VAL_UUID, sensor_cleaner)



# 								#
#			ATTACHMENTS			# 
# 								#

""" Parent class for anything that is plugged into the Hub's ports """
class Attachment():
	def __init__(self, client=None, port=None):
		self.client = client
		self.port = port

""" Parent class for anything that reads values """
class Sensor(Attachment):
	async def read_value(self):
		await self.client.read_gatt_char(SENSOR_VAL_UUID, True)

	async def set_mode(self, mode):
		pass

class DistanceSensor(Sensor):
	"""
	Set the distance sensor to one of two modes:
		DIST_DETECT_MODE - report distance from object from 1-10
		DIST_COUNT_MODE - ???
	"""
	async def set_mode(self, mode):
		data = bytearray( [0x01,0x02,self.port,0x23,mode,0x01,0x00,0x00,0x00,0x02,0x01] )
		await self.client.write_gatt_char(INPUT_COMMAND_UUID, data, True)

class TiltSensor(Sensor):
	"""
	Set the tilt sensor to one of three modes:
		TILT_ANGLE_MODE - ???
		TILT_TILT_MODE - report one of six "tilt states" (neutral, forward, backward, etc.)
		TILT_CRASH_MODE - ???
	"""
	async def set_mode(self, mode):
		data = bytearray( [0x01,0x02,self.port,0x22,mode,0x01,0x00,0x00,0x00,0x02,0x01] )
		await self.client.write_gatt_char(INPUT_COMMAND_UUID, data, True)

class Motor(Attachment):
	"""
	Set the speed of the motor, from 1 to -1 (0=stopped)
	"""
	async def set_speed(self, speed, factor=1):
		data = bytearray([self.port, 0x01, 0x01, self.translate_speed( speed, factor) ])

		await self.client.write_gatt_char(OUTPUT_COMMAND_UUID, data, True )

	def translate_speed(self, speed, factor=1):
	    if speed < 0:
	        return int((0x54*max(speed,-1)*factor)+0xF0)
	    elif speed > 0:
	        return int((0x54*min(speed,1)*factor)+0x10)
	    else:
	        return 0x00
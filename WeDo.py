import pygatt

class Smarthub:
	def __init__ (self, mac):
		self.address = mac
		self.adapter = pygatt.GATTToolBackend()

	def connect (self):
		self.adapter.start()
		self.device = self.adapter.connect(self.address)

	def send_data (self, handle, data):
		self.device.char_write_handle(handle, bytearray(data))

class Motor:
    
    def __init__(self, port, master):
        if not (port == 1 or port == 2):
            raise Exception('The port for a motor must be 01 or 02')
        self.port = port
        self.master = master
        self.handle = 0x3d
    
    def set_speed(self, speed):
        self.master.send_data(self.handle, [self.port, 1, 1,self.translate_speed(speed)])
        
    def translate_speed(self, speed):
        if speed < 0:
            return int((0x54*max(speed,-1))+0xF0)
        elif speed > 0:
            return int((0x54*min(speed,1))+0x10)
        else:
            return 0x00
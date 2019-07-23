import pygatt, abc

class Smarthub:
    def __init__ (self, mac):
        self.address = mac
        self.adapter = pygatt.GATTToolBackend()

        self.ports = [None] * 2

    def connect (self):
        self.adapter.start()
        self.device = self.adapter.connect(self.address)

    def send_data (self, handle, data):
        self.device.char_write_handle(handle, bytearray(data))
    
    def disconnect (self):
        self.device.disconnect()

    def attach_port (self, port, Type):
        self.ports[port-1] = Type(port, self)

    def get_port (self, port):
        return self.ports[port-1]


class Attachment (abc.ABC):
    def __init__ (self, port, master):
        if not (port == 1 or port == 2):
            raise Exception('The port for a motor must be 01 or 02')
        self.port = port
        self.master = master


class Motor(Attachment):
    def __init__(self, port, master, factor):
        Attachment.__init__(self, port, master)
        self.factor = factor
        self.handle = 0x3d
    
    def set_speed(self, speed):
        self.master.send_data(self.handle, [self.port, 1, 1,self.max_speed(speed)])
        self.master.send_data(self.handle, [self.port, 1, 1,self.translate_speed(speed)])
        
    def translate_speed(self, speed):
        if speed < 0:
            return int((0x54*max(speed,-1)*self.factor)+0xF0)
        elif speed > 0:
            return int((0x54*min(speed,1)*self.factor)+0x10)
        else:
            return 0x00

    def max_speed(self, speed):
        if speed < 0:
            return int(0xC6)
        elif speed > 0:
            return int(0x3A)
        else:
            return 0

class Sensor(Attachment):
    def __init__(self, port, master):
        Attachment.__init__(self, port, master)
        
        self.handle = 0x32

    def read(self):
        output = self.master.read(self.handle, self.port)
        process(output)

    @abc.abstractmethod
    def process(output):
        # process the output to something meaningful
        pass

class TiltSensor(Sensor):
    def __init__(self, port, master):
        Sensor.__init__(self,port,master)
        # Set to tilt mode
        self.master.send_data(0x3a, [0x01,0x02,0x01,0x22,0x01,0x01,0x00,0x00,0x00,0x02,0x01]) 

    def process(output):
        print(output)

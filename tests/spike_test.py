
import hub, utime

def IDWeDo(devices):
     reply = False
     for device in devices:
          service_id = device["service_id"]
          if service_id.find('00001623') >= 0:
               print(service_id)
               reply = True
     return reply
               
def dump_data(d):
    print("CB z:", ' '.join(['0x%02X ' % (byte) for byte in d]))

def connect_callback(a):
     print('Connection complete: {0}'.format(a))
          
hub.ble.mac()

hub.ble.rssi(-50)
hub.ble.scan(10)
f = hub.ble.scan_result()

while not IDWeDo(f):
     f = hub.ble.scan_result()
     utime.sleep(0.2)

hub.ble.callback(connect_callback)

g = hub.ble.connect(0)

utime.sleep(10)

pink = bytes([0x06, 0x04, 0x01, 0x01])  
#06 is the port number (internal LED), 04 is the command number (change light color), 01 is the command size (only 1 argument), and 01 is the command value (color)
g.send(bytearray[0x00, 0x08, 04, 0x06, 00, 0x3d, 0x00, 0x04, 0x06, 0x04, 0x01, 0x04])

g.callback(dump_data)

g.subscribe()

utime.sleep(10)

g.unsubscribe()

f.disconnect()


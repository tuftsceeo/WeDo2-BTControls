from WeDo import *
import time

hub = Smarthub('24:71:89:17:9D:AE')
hub.connect()

hub.attach_port(2, Motor)

hub.get_port(2).set_speed(0.1)

time.sleep(5)

hub.get_port(2).set_speed(0)

hub.disconnect()
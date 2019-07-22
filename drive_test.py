from WeDo import *
import time

hub = Smarthub('24:71:89:09:CB:21')
hub.connect()

m1 = Motor(1, hub)
m2 = Motor(2, hub)

m1.set_speed(-1)
m2.set_speed(1)

time.sleep(10)

m1.set_speed(-1)
m2.set_speed(1)

time.sleep(10)

m1.set_speed(0)
m2.set_speed(0)
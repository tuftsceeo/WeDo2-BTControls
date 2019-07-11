from WeDo import Smarthub, Motor
import time

myhub = Smarthub('24:71:89:17:9D:AE')

myhub.connect()

mot1 = Motor(2, myhub)

	
for i in range(9):
	mot1.set_speed((float(i)-4)/4)
	time.sleep(1)
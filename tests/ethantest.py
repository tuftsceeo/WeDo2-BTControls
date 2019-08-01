# Import WeDo2.py from the parent directory
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))from WeDo2 import *
import asyncio as aio# Queues to store updates from the distance sensor
TILT_PORT_NUM = 1
tilt_q = aio.Queue()motor_speed1 = 0
motor_speed2 = 0"""
This function is called when the distance sensor updates
   hub - the distance sensor's hub
   port - the port the distance sensor is on
   num - the value it reported
"""
def tilt_callback (hub, port, num):
   tilt_q.put_nowait(num)""" The main loop for the program """
async def main ():
   global tilt_q, motor_speed1, motor_speed2    
   """
   The WeDo setup:
   - 1 WeDo with only a distance sensor attached on port 1 (brain, have it connect first)
   - 1 WeDo with two motors attached (driver)
   """
   h = HubManager(2)    # Search and establish connections w/ WeDos
   await h.connect_all(['0C:61:CF:C9:B0:39'])
   brain = h.wedos[1]
   driver = h.wedos[0]    # Register the distance sensor in port 1 of the brain
   
   t_sensor = await brain.attach(TILT_PORT_NUM, TiltSensor())    # Register motors
   
   m1 = await driver.attach(1, Motor())
   
   m2 = await driver.attach(2, Motor())    # Detect mode reports distsance to nearest object, from 1-10
   
   await t_sensor.set_mode(TILT_TILT_MODE)    # When the sensor on port 1 receives an update, call dist_callback
   await brain.set_sensor_callback(TILT_PORT_NUM, tilt_callback)    

   while True:
       # Every loop check if the quit key has been press (q-Enter)
       await h.end(False)        try:
           t = tilt_q.get_nowait()
           direction = 'UNKNOWN'            if t == TILT_SENSOR_DIRECTION_NEUTRAL:
               direction = 'NEUTRAL'
               motor_speed1 = 0
               motor_speed2 = 0
           elif t == TILT_SENSOR_DIRECTION_BACKWARD:
               direction = 'BACKWARD'
               motor_speed1 = -1
               motor_speed2 = -1
           elif t == TILT_SENSOR_DIRECTION_RIGHT:
               direction = 'RIGHT'
               motor_speed1 = 1
               motor_speed2 = -1
           elif t == TILT_SENSOR_DIRECTION_LEFT:
               direction = 'LEFT'
               motor_speed1 = -1
               motor_speed2 = 1
           elif t == TILT_SENSOR_DIRECTION_FORWARD:
               direction = 'FORWARD'
               motor_speed1 = 1
               motor_speed2 = 1            print(t, direction)            #print(f'Got an update: {motor_speed}!')
       except aio.QueueEmpty:
           pass        # Set motors' speeds
       await m1.set_speed(motor_speed1)
       await m2.set_speed(motor_speed2)        # Allow some buffer time between each loop
       await aio.sleep(0)# loop from the WeDo2 library, run the main function
loop.run_until_complete(main())
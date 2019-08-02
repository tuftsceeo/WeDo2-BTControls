# Import WeDo2.py from the parent directory
import os, sys, time, colorsys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WeDo2 import *
import asyncio as aio

location = 0
duration = 1000
lastTime = time.time()
# Queues to store updates from the distance sensor


""" The main loop for the program """
async def main ():
        global lastTime, duration, location

        h = HubManager(1)
	
	# Search and establish connections w/ WeDos
        await h.connect_all(['A0:E6:F8:1B:7A:FC']) #replace this with the macaddresses of the WeDos you are using

        hub = h.wedos[0]

        await hub.set_led_mode(LED_DISCRETE_MODE)
        

        while True:
            # Every loop check if the quit key has been press (q-Enter)
            await h.end(False)
            currentTime = time.time()
            location = location + currentTime - lastTime if location < duration else 0
            lastTime = currentTime

            hue = 360 * location / duration
            rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue, 1, 1))
            await hub.set_led_color(rgb)

            # Allow some buffer time between each loop
            await aio.sleep(0)

# loop from the WeDo2 library, run the main function
loop.run_until_complete(main())

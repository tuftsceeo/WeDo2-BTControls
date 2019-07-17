# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

import sensor, image, time, LPF2Class

lpf2 = LPF2(3, 'P4', 'P5', timer = 4, freq = 5)    # OpenMV UART #, Tx, Rx, callback timer, and timer frequency
lpf2.initialize()

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

while(True):
    if not lpf2.connected:
        lpf2.sendTimer.callback(None)   # clear any earlier          
        utime.sleep_ms(200)
        lpf2.initialize()
    else:
        clock.tick()                    # Update the FPS clock.
        img = sensor.snapshot()         # Take a picture and return the image.
        rgb = img.get_pixel(int(img.width()/2), int(img.height()/2))
        rgb8 = (int(rgb[0] / 32) << 5) + (int(rgb[1]  / 32) << 2) + int(rgb[2] / 64)
        print(rgb8)                   
        lpf2.load_payload(rgb8)
        data = lpf2.readIt()
        
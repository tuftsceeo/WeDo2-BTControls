import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(10)
sensor.set_gain_ctrl(False)
clock = time.clock()

while True:
	clock.tick()
	img = sensor.snapshot()
	img.lens_corr(1.6)
	for code in img.find_qrcodes():
		print(code)
	print(clock.fps())
import machine, utime, gc

from pyb import LED

red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)

class LPF2(object):
     def __init__(self, uartChannel, txPin, rxPin):
          self.txPin = txPin
          self.rxPin = rxPin
          self.uart = machine.UART(uartChannel)
          self.connected = False

     def send_value(self,data):
          value = (data & 0xFF)
          payload = bytes([0xC0, value, 0xFF ^ 0xC0 ^ value])
          size = self.uart.write(payload)
          if not size: self.connected = False

     def initialize(self):
          self.tx = machine.Pin(self.txPin, machine.Pin.OUT)
          self.rx = machine.Pin(self.rxPin, machine.Pin.IN)
          self.tx.value(0)
          utime.sleep_ms(500)
          self.tx.value(1)
          self.uart.init(baudrate=2400, bits=8, parity=None, stop=1)
          self.uart.write(b'\x00')
          self.uart.write(b'\x40\x23\x9C')
          self.uart.write(b'\x49\x02\x01\xB5')
          self.uart.write(b'\x52\x00\xC2\x01\x00\x6E')
          self.uart.write(b'\x5F\x00\x00\x00\x02\x00\x00\x00\x02\xA0')
          self.uart.write(b'\x9A\x00\x4C\x50\x46\x32\x2D\x43\x41\x4C\x6E')
          self.uart.write(b'\x9A\x01\x00\x00\x00\x00\x00\xC0\x7F\x44\x9F')
          self.uart.write(b'\x9A\x02\x00\x00\x00\x00\x00\x00\xC8\x42\xED')
          self.uart.write(b'\x9A\x03\x00\x00\x00\x00\x00\xC0\x7F\x44\x9D')
          self.uart.write(b'\x92\x04\x52\x41\x57\x00\x2D')
          self.uart.write(b'\x8A\x05\x10\x00\x60')
          self.uart.write(b'\x92\x80\x03\x01\x03\x00\xEC')
          utime.sleep_ms(5)
          #  print(uart.read(uart.any()))
          self.uart.write(b'\xA1\x00\x4C\x50\x46\x32\x2D\x43\x4F\x55\x4E\x54\x00\x00\x00\x00\x00\x00\x58')
          self.uart.write(b'\x99\x01\x00\x00\x00\x00\x00\x00\xC8\x42\xED')
          self.uart.write(b'\x99\x02\x00\x00\x00\x00\x00\x00\xC8\x42\xEE')
          self.uart.write(b'\x99\x03\x00\x00\x00\x00\x00\x00\xC8\x42\xEF')
          self.uart.write(b'\x91\x04\x43\x4E\x54\x00\x33')
          self.uart.write(b'\x89\x05\x10\x00\x63')
          self.uart.write(b'\x91\x80\x01\x02\x04\x00\xE9')
          utime.sleep_ms(5)
          # print(uart.read(uart.any()))
          self.uart.write(b'\xA0\x00\x4C\x50\x46\x32\x2D\x44\x45\x54\x45\x43\x54\x00\x00\x00\x00\x00\x1D')
          self.uart.write(b'\x98\x01\x00\x00\x00\x00\x00\x00\x20\x41\x07')
          self.uart.write(b'\x98\x02\x00\x00\x00\x00\x00\x00\xC8\x42\xEF')
          self.uart.write(b'\x98\x03\x00\x00\x00\x00\x00\x00\x20\x41\x05')
          self.uart.write(b'\x80\x04\x00\x7B')
          self.uart.write(b'\x88\x05\x10\x00\x62')
          self.uart.write(b'\x90\x80\x01\x00\x03\x00\xED')
          utime.sleep_ms(5)
          # print(uart.read(uart.any()))
          self.uart.write(b'\x04')
          # wait for ACK
          starttime = utime.time()
          currenttime = starttime
          while (currenttime-starttime) < 2000:
               utime.sleep_ms(5)
               data = self.uart.read(self.uart.any())
               if data.find(b'\x04') >= 0:
                    self.connected = True
                    currenttime = starttime+3000   # stop the loop
               else:
                    currenttime = utime.time()
          # pull pin low
          self.uart.deinit()
          self.tx = machine.Pin(self.txPin, machine.Pin.OUT)
          self.tx.value(0)
          utime.sleep_ms(10)
          #change baudrate
          self.uart.init(baudrate=115200, bits=8, parity=None, stop=1)

from pyb import LED
import sensor

send_nums = {
  'PINK': 0,
  'PURPLE': 10,
  'BLUE': 20,
  'GREEN': 30,
  'ORANGE': 40
}

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# loop from -10 to 10
red_led = LED(1)
i=0
red_led.on()
print("hi")
lpf2 = LPF2(3, 'P4', 'P5')    # OpenMV
lpf2.initialize()
print("initialized")

while True:
     if not lpf2.connected:
          red_led.on()
          utime.sleep(1)
          lpf2.initialize()
     else:
          red_led.off()

          while lpf2.connected:
               #i = 0
               gc.collect()
               img = sensor.snapshot()
               img.lens_corr(1.6)
               for code in img.find_qrcodes():
                            key = code.payload().upper()
                            try:
                                print(key, send_nums[key])
                                i = send_nums[key]
                            except KeyError:
                                pass
               print(i)
               lpf2.send_value(i)
               #print(i)
               #print(lpf2.connected)
               #if i >= 255: i=0
               #utime.sleep_ms(200)
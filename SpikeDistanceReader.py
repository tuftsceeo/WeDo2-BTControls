import hub,utime, time, math

hub.port.B.info()
# if info comes back with None - then you have to restart the microprocessor

memory = []
dHeightCM = 9
while True:  
     try:
          if hub.port.B.device == None:
               print('no device in port b')
          if hub.port.D.device == None:
               print('no device in port d')
          
          bot = hub.port.B.device.get()[0]
          top = hub.port.D.device.get()[0]
          
          print(bot, top)
          if not ( top == -1 or bot == -1 or bot > top):
               difference = top - bot
               distanceCM = (80*dHeightCM) / (difference * math.tan(27.8*math.pi/180))
               distanceIN = distanceCM/2.54
               
               memory.append(distanceIN)
               if len(memory) > 10:
                    memory.pop(0)
               
               
               print(str(sum(memory)/len(memory)) + ' inches away')
               
          #hub.display.show(str(value))
          utime.sleep(0.05)

     except:
          utime.sleep(0.5)

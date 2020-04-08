import paho.mqtt.client as mqtt
from hardware import hardware
from datetime import timedelta
import time
import threading

import logout
import atexit
import signal
import sys
from scheduler import Schedule

class hardwareCommunication():

  def __init__(self):
    self.msg=''
    self.interval = 0.0
    self.receivedHWCommand = False

    # create hardwareInstance
    self.hardware = hardware()

    # create and start Threads
    self.runThread = Schedule(interval=timedelta(seconds=self.interval), execute=self.hardwareThread)
    #self.runThread.start()

    # mqtt Client
    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message 

    try:
      self.client.connect("localhost", 1883, 60)
    except Exception as e:
      print("connection failed!")
      exit(1)

    self.client.loop_forever()


  def __del__(self):
    print('ending')
    self.client.disconnect()
    del self.hardware


  def on_connect(self, client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("HW/Commands")

  def on_message(self, client, userdata, msg):
    data = msg.payload
    decodedData = data.decode('utf-8')

    if decodedData == "start":
      print('received Msg: start')
      self.runThread.start()
      self.runThread.do_run = True

    elif decodedData == "stop":
      print('received Msg: stop')
      self.runThread.do_run = False
      self.runThread.stop()

    elif decodedData == "exit":
      print('received Msg: exit')
      del self.hardware
      
    elif decodedData == '':
      print('msg empty')
    
    else: 
      print('received Msg: A..:..:..')
      self.receivedHWCommand = True
      self.msg = decodedData.replace('A', '').split(':')
      print('')


  def hardwareThread(self):
    cc = 0
    while getattr(self.runThread, "do_run", True):
      cc += 1
      if cc % 100 == 0:
        print('Publishing registers')
        regs = self.hardware.readAddresses(0, 10)
        self.client.publish('HW/Publish', str(regs))
        time.sleep(0.001)

      if self.receivedHWCommand == True:
        print('writing bits to hardware')
        ret = self.hardware.writeBits(self.msg)
        print(ret)
        self.receivedHWCommand = False
      
      time.sleep(0.001)

if __name__ == "__main__":
  hwComThread = hardwareCommunication()

  # except(ProgramKilled):
  #   hwComThread.runThread.stop()
  #   #hwComThread.messageThread.stop()
  #   del hwComThread.hardware
  #   print('program exited')


# class ProgramKilled(Exception):
#     pass

# def sendMsg():
#   # create client
#   client = mqtt.Client()
#   try:
#     client.connect("localhost", 1883, 60)
#   except Exception as e:
#     print("connection failed!")
#     exit(1)
#   cc = 0
#   timeout = time.time() + 5
#   whiletrue = True  
#   while whiletrue:
#     if time.time() < timeout:
#       client.publish('HW/Commands', 'A0:8:' + str(cc), qos=2)
#       client.loop(2, 10)
#       time.sleep(0.002)
#       cc+=1
#       if cc > 127:
#         cc = 0

#     else:
#       client.publish('HW/Commands', 'stop')
#       whiletrue = False

# except ProgramKilled:
#   print('runThread stopped')
#   #self.runThread.stop()
#   #cleanup
#   break
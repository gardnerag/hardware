import json
from collections import OrderedDict
import hardwareModbus
import importlib
import logout
import ast
import numpy
import copy
import time
class hardware():

  def __init__(self):
    self.deviceName, self.configFile, self.inBufferLength, self.outBufferLength = self.readConfig()
    self.hardwareInstance = self.getHardwareInstance()
    self.log = logout.logout()
    self.outBufferBytes = [0 for i in range(int(self.outBufferLength))]
    self.outBufferBits = [[0 for i in range(8)] for i in self.outBufferBytes]
    self.outputs = self.readOutBuffTxt()
    print('')

  def __del__(self):
    print('In hardware.__del__')
    del self.hardwareInstance

  def readConfig(self):
    configFile = "config.json"
    f = open("config.json")
    configFile = json.load(f, object_pairs_hook=OrderedDict)
    deviceName = next(iter(configFile))
    inBufferLength = configFile['Hardware']['inBufferLength']
    outBufferLength = configFile['Hardware']['outBufferLength']
    return deviceName, configFile, inBufferLength, outBufferLength

  def getHardwareInstance(self):
    moduleName = 'hardware' + self.deviceName
    module = importlib.import_module(moduleName)
    class_ = getattr(module, moduleName)
    instance = class_(self.configFile)
    return instance

  def readOutBuffTxt(self):
    with open('outBuffer.txt') as f:
      content = f.readline()
    if content == '':
      content = self.outBufferBytes
    else:
      content = ast.literal_eval(content)
      while len(content) < 20:
        content.append(False)
    return content

  # WRITE Bits / Registers
  def writeBit(self, address, bitValue):
    status = self.hardwareInstance.writeBit(address, bitValue)
    return status

  def writeBits(self, msg):
    start = time.time()
    tempOutBufferBits = self.setBits(msg)
    self.bitsToBytes(tempOutBufferBits)
    end = time.time()
    print(end-start)

    ret = self.hardwareInstance.writeBits(self.outBufferBytes)
    return ret
    
  def setBits(self, msg):
    if msg == '':
      time.sleep(0.1)

    else:
      if len(msg) == 2:
        startAddr, value = msg[0].split('.'), int(msg[1])
        noBits = (value).bit_length()

      else:    
        startAddr, value, noBits = msg[0].split('.'), int(msg[1]), int(msg[2])    #A    0.6     :   1   :   4
        
      startAddr = [int(i) for i in startAddr]    
      value = bin(value).replace('0b', '')

      if startAddr[1] > 7 or startAddr[0] > (int(self.outBufferLength) -1): 
        print('Error start address wrong')

      # Create Mask
      mask = []
      for char in value:
        mask.append(int(char))
      mask.reverse()
      while len(mask) < noBits:
        mask.append(0)

      else:
        for index, i in enumerate(self.outBufferBits[startAddr[0]]):
          if index == startAddr[1]:
            # ONE BYTE
            if (startAddr[1] + noBits) <= 8: 
              #first byte
              for j in mask:
                self.outBufferBits[startAddr[0]][startAddr[1]] = j
                mask = list(mask)
                mask.remove(mask[0])
                startAddr[1] += 1
                if len(mask) == 0:
                  tempOutBufferBits =  copy.deepcopy(self.outBufferBits)
                  return tempOutBufferBits
            
            # TWO BYTES
            if (startAddr[1] + noBits) > 8 and (startAddr[1] + noBits) <= 16:
              #first byte
              for j in mask:
                self.outBufferBits[startAddr[0]][startAddr[1]] = j
                mask = list(mask)
                mask.remove(mask[0])
                startAddr[1] += 1

                #second byte
                if startAddr[1] == 8:
                  for index, i in enumerate(self.outBufferBits[startAddr[0] + 1]):
                    for j in mask:
                      self.outBufferBits[startAddr[0] + 1][index] = j
                      mask = list(mask)
                      mask.remove(mask[0])
                      startAddr[1] += 1
                      if len(mask) == 0:
                        tempOutBufferBits =  copy.deepcopy(self.outBufferBits)
                        return tempOutBufferBits
                      break
            
            # THREE BYTES
            if (startAddr[1] + noBits) > 16:
              #first byte
              for j in mask:
                self.outBufferBits[startAddr[0]][startAddr[1]] = j
                mask = list(mask)
                mask.remove(mask[0])
                startAddr[1] += 1

                #second byte
                if startAddr[1] == 8:
                  for index, i in enumerate(self.outBufferBits[startAddr[0] + 1]):
                    for j in mask:
                      self.outBufferBits[startAddr[0] + 1][index] = j
                      mask = list(mask)
                      mask.remove(mask[0])
                      startAddr[1] += 1

                      #third byte
                      if startAddr[1] == 16:
                        for index, i in enumerate(self.outBufferBits[startAddr[0] + 2]):
                          for j in mask:
                            self.outBufferBits[startAddr[0] + 2][index] = j
                            mask = list(mask)
                            mask.remove(mask[0])
                            startAddr[1] += 1
                            if len(mask) == 0:
                              tempOutBufferBits =  copy.deepcopy(self.outBufferBits)
                              return tempOutBufferBits
                            break
                      break
        return False 

  def bitsToBytes(self, tempOutBufferBits):
    for index, lis in enumerate(tempOutBufferBits):
      for i, item in enumerate(lis):
        lis[i] = str(item)
      tempOutBufferBits[index] = ''.join(lis)

    self.outBufferBytes = [int(i, 2) for i in tempOutBufferBits]


  def writeAddress(self, regAddress, regValue):
    status = self.hardwareInstance.writeAdress(regAddress, regValue)
    return status

  def writeAddresses(self, regAddress, regValue):
    status = self.hardwareInstance.writeAddresses(regAddress, regValue)
    return status

  # READ Bits / Registers
  def readBits(self, address, bitNumber):
    status = self.hardwareInstance.readBits(address, bitNumber)
    return status

  def readAddresses(self, regAddress, regNumber):
    status = self.hardwareInstance.readAddresses(regAddress, regNumber)
    return status
  
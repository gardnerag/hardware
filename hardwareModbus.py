from pyModbusTCP.client import ModbusClient
import logout
import time
import numpy

class hardwareModbus():
  def __init__(self, configFile):
    self.configFile = configFile
    self.host, self.port = self.readConfig()
    self.modbus = ModbusClient()
    self.modbus.host(self.host)
    self.modbus.port(self.port)
    self.modbus.open()
    self.resetWatchdog()
    self.log = logout.logout()

  def __del__(self):
    print('in hardwareModbus.__del__')

    open('outBuffer.txt', 'w').close()
    with open('outBuffer.txt', 'w') as f:
      f.write(str(self.outputs))

    self.modbus.close()  

  def readConfig(self):
    deviceName = next(iter(self.configFile))
    host = self.configFile[deviceName]['host']
    port = self.configFile[deviceName]['port']
    return host, port

  def bytesToBits(self, outputBytes):
    test =  numpy.unpackbits(numpy.array(outputBytes, dtype = numpy.uint8))
    typee = type(test)
    testList = list(test)
    teyeof = type(testList)
    boolList = []
    for i in testList:
      if i == 0:
        boolList.append(False)
      else:
        boolList.append(True)

    return boolList

  # RESET Watchdog
  def resetWatchdog(self):
    self.modbus.write_single_register(4384, 0)
    
  # WRITE Bits / Registers
  def writeBit(self, address, bitValue):
    self.modbus.write_single_coil(address, bitValue)

  # for Dummy test
  def byteChunks(self, lst, n):
    final = [lst[i * n:(i + 1) * n] for i in range((len(lst) + n - 1) // n )]  
    return final

  def writeBits(self, outputBytes):
    self.outputs = outputBytes
    boolList = self.bytesToBits(outputBytes)
    ret = self.modbus.write_multiple_coils(0, boolList)
    return ret

  def writeAdress(self, regAddress, regValue):
    self.modbus.write_single_register(regAddress, regValue)

  def writeAddresses(self, regAddress, regValue):
    self.modbus.write_multiple_registers(regAddress, regValue)
  
  # READ Bits / Registers
  def readBits(self, address, bitNumber):
    self.modbus.read_coils(address, bitNumber)
  
  def readAddresses(self, regAddress, regNumber):
    regs = self.modbus.read_holding_registers(regAddress, regNumber)
    self.log.log('In hardwareModbus.readMultipleAddresses() \n'  + str(regs) + '\n' + 'address: ' + str(regAddress) + '\n')
    return regs

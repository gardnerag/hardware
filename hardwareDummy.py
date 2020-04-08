import logout

class hardwareDummy():

  #TODO: dummyTestFile may have to be split into ranges of interesting address regions of the hardware.

  def __init__(self, configFile):
    self.configFile = configFile
    self.noOfInBytes, self.noOfOutBytes = self.readConfig()
    
    oneByte = [0 for i in range(0, 8)]
    self.dummyOut = [oneByte for i in range(0, int(self.noOfOutBytes))]
    self.log = logout.logout()
    
  def __del__(self):
    open('outBuffer.txt', 'w').close()
    with open('outBuffer.txt', 'w') as f:
      f.write(str(self.outputs))
    self.close() 

  def readConfig(self):
    deviceName = next(iter(self.configFile))
    noOfInBytes = self.configFile[deviceName]['noOfInBytes']
    noOfOutBytes = self.configFile[deviceName]['noOfOutBytes']
    return noOfInBytes, noOfOutBytes
      

  def byteChunks(self, lst, n):
    final = [lst[i * n:(i + 1) * n] for i in range((len(lst) + n - 1) // n )]  
    return final

  def writeBits(self, outputBytes):
    return outputBytes

  def readAddresses(self, regAddress, regNumber):
    pass


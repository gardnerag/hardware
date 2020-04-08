import json
import hardwareModbus

class confHardware():

    def __init__(self, hardwareDevice):         #hardwaredevice = modbus

        self.hardwareDevice = hardwareDevice
        
        if hardwareDevice == "modbus":
            self.SERVER_HOST, self.SERVER_PORT = readConfig()
            self.hardware = hardwareModbus(self.SERVER_HOST, self.SERVER_PORT)

    def readConfig():
        configFile = "config.json"
        f = open("config.json")
        configFile = json.load(f)
        host = configFile[self.hardwareDevice]['host']
        port = configFile[self.hardwareDevice]['port']

        return host, port

if __name__ == "__main__":
    confHW = confHardware()
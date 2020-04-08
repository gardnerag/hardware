from pyModbusTCP.client import ModbusClient
import time
import threading
import sys
import paho.mqtt.client as mqtt

status = True

class hardwareMonitor():

    def __init__(self):
        
        self.block = False
        self.outBuffer = [False for i in range(0, 16)]
        self.t = threading.Thread(target=self.monitorInputs, args=("task",))
        
        #Modbus
        self.SERVER_HOST = "192.168.178.88"
        self.SERVER_PORT = 502
        self.modbus = ModbusClient()
        self.openModbus()

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
        self.client.disconnect()
        self.modbus.close()

    def openModbus(self):
        self.modbus.host(self.SERVER_HOST)
        self.modbus.port(self.SERVER_PORT)
        self.modbus.open()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("HW/Commands")
        
    def on_message(self, client, userdata, msg):
        data = msg.payload
        print('message: ' + str(data) + ' ' + str(userdata))

        if str(data) == "b'start'":
            self.t.start()
            print("Started monitorInputs()")
            #time.sleep(6)

        elif str(data) == "b'stop'":
            print('message stop')
            self.t.do_run = False
            self.t.join()
        
        else: 
            msg = data.decode('utf-8').replace('A', '').split(':')       

            startAddr = int(msg[0])
            noBits = int(msg[1])
            value = int(msg[2])

            tempBuff = list(bin(value)[2:])
            tempBuff.reverse()
            while len(tempBuff) < noBits:
                tempBuff.append('0')
           
            for i in tempBuff:
                boolBuff = [True if i == '1' else False for i in tempBuff]

            for adX, output in enumerate(self.outBuffer):
                if adX >= startAddr and adX <= startAddr + (noBits - 1):
                    self.outBuffer[adX] = boolBuff[adX-startAddr]

                self.switchOutput(int(msg[0]), True)
            else:
                self.switchOutput(int(msg[0]), False)


    def monitorInputs(self, arg):
        self.resetWatchdog()

        while getattr(self.t, "do_run", True):
            if not self.block:
                # ausgangsbuffer schreiben
                ret = self.modbus.write_multiple_coils(0, self.outBuffer)
                print(ret)
                # read 10 registers at address 0, store result in regs list
                regs = self.modbus.read_holding_registers(0, 10)
                self.client.publish('HW/Publish', str(regs))
                #print(regs)

            #print('sleeping')
            time.sleep(0.01)

    def switchOutput(self, outputAddr, status):
        # read 10 registers at given address, store result in regs list
        self.outBuffer[outputAddr] = bool(status)

    def resetWatchdog(self):
        reg = self.modbus.write_single_register(4384, 0)


if __name__ == "__main__":
    hwM = hardwareMonitor()

from datetime import datetime

class logout():
    def __init__(self):
        self.filename = "hardware.log"
        open(self.filename, 'w').close()

    def log(self, msg):
        f = open(self.filename, 'a')
        dateTimeObj = str(datetime.now())
        f.write(dateTimeObj + ' ' + msg + '\n')

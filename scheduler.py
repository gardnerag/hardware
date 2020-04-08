# =============================================================================
# Copyright (c) 2018-2019 gardner ag. All Rights Reserved.
#
# This software is the confidential and proprietary information of gardner ag
# ("Confidential Information"). You shall not disclose such 
# Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with gardner ag.
#
# GARDNER AG MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. GARDNER AG SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
import threading, time, signal
from datetime import timedelta

class Schedule(threading.Thread):
  def __init__(self, interval, execute, *args, **kwargs):
    threading.Thread.__init__(self)
    self.daemon = False
    self.stopped = threading.Event()
    self.interval = interval
    self.execute = execute
    self.args = args
    self.kwargs = kwargs
      
  def stop(self):
    self.stopped.set()
    self.join()

  def run(self):
    while not self.stopped.wait(self.interval.total_seconds()):
      self.execute(*self.args, **self.kwargs)

class ProgramKilled(Exception):
    pass

def signal_handler(signum, frame):
    raise ProgramKilled

def foo():
    print(time.ctime())

WAIT_TIME_SECONDS = 1

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Schedule(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=foo)
    job.start()
    
    while True:
          try:
              time.sleep(1)
          except ProgramKilled:
              print("Program killed: running cleanup code")
              job.stop()
              break

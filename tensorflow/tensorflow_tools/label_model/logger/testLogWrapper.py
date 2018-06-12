
import logging
from logWrapper import *
import time

if __name__ == "__main__":
    for num in range(1, 9999999):
        LogWrapper.init("ddiv"+str(time.time())+".log")
        # LogWrapper.init("log.log","M",1,2)
        LogWrapper.set_level(logging.INFO)
        logging.debug('This is debug message')
        logging.info('This is info message')
        logging.warning('This is warning message %d %s', 55, "fff")
        time.sleep(1)

